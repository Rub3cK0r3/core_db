import asyncio
import asyncpg
import json
import signal

REQUIRED_EVENT_FIELDS = ["type", "payload"]

class AsyncCollector:
    def __init__(self, db_dsn, max_queue_size=1000, worker_count=4):
        self.db_dsn = db_dsn
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.worker_count = worker_count
        self.workers = []
        self.listener_task = None
        self.db_pool = None
        self.shutdown_event = asyncio.Event()

    # =========================
    # START
    # =========================
    async def start(self):
        # Crear pool de DB
        self.db_pool = await asyncpg.create_pool(dsn=self.db_dsn)
        print(f"DB pool created with {self.worker_count} workers.")

        # Lanzar listener async
        self.listener_task = asyncio.create_task(self._listener_loop())

        # Lanzar workers async
        for _ in range(self.worker_count):
            worker_task = asyncio.create_task(self._worker_loop())
            self.workers.append(worker_task)

        print("AsyncCollector started.")

    # =========================
    # LISTENER LOOP (PostgreSQL NOTIFY)
    # =========================
    async def _listener_loop(self):
        while not self.shutdown_event.is_set():
            try:
                async with self.db_pool.acquire() as conn:
                    # Escuchar canal 'events_channel'
                    await conn.add_listener("events_channel", self._notify_callback)
                    while not self.shutdown_event.is_set():
                        await asyncio.sleep(1)  # Mantener el loop vivo

            except Exception as e:
                print("Listener error:", e)
                await asyncio.sleep(2)  # Retry lento

    # =========================
    # CALLBACK por cada notificación
    # =========================
    def _notify_callback(self, connection, pid, channel, payload):
        try:
            event = json.loads(payload)
            if not self._validate_event(event):
                print("Invalid event, skipping:", event)
                return
            # Poner en la cola async sin bloquear
            asyncio.create_task(self.queue.put(event))
        except json.JSONDecodeError:
            print("Invalid JSON payload:", payload)

    # =========================
    # WORKER LOOP (async)
    # =========================
    async def _worker_loop(self):
        while not self.shutdown_event.is_set() or not self.queue.empty():
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=1)
                await self._process_event_db(event)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print("Worker error:", e)

    # =========================
    # Procesamiento con transacción
    # =========================
    async def _process_event_db(self, event):
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        "INSERT INTO events(type, payload) VALUES($1, $2)",
                        event["type"], json.dumps(event["payload"])
                    )
            print("Processed event:", event)
        except Exception as e:
            print("DB write failed for event:", event, "Error:", e)

    # =========================
    # Validación mínima
    # =========================
    def _validate_event(self, event):
        return all(field in event for field in REQUIRED_EVENT_FIELDS)

    # =========================
    # GRACEFUL SHUTDOWN
    # =========================
    async def stop(self):
        print("Collector stopping...")
        self.shutdown_event.set()

        # Esperar a que la cola se drene
        await self.queue.join()

        # Cancelar listener
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        # Cancelar workers
        for w in self.workers:
            w.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)

        # Cerrar pool DB
        await self.db_pool.close()
        print("Collector stopped gracefully.")


# =========================
# MAIN
# =========================
async def main():
    collector = AsyncCollector(db_dsn="postgres://user:pass@localhost/db", worker_count=4) # CAMBIAR POR LOS DEL ENTORNO PostgreSQL
    await collector.start()

    # Manejar SIGINT/SIGTERM para shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    await collector.stop()

if __name__ == "__main__":
    asyncio.run(main())

