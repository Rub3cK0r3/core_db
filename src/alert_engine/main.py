import asyncio
import asyncpg
import json
import signal

REQUIRED_ALERT_FIELDS = ["id", "severity", "resource"]

class AsyncAlertManager:
    def __init__(self, db_dsn, channel="canal_eventos", max_queue_size=1000, worker_count=2):
        self.db_dsn = db_dsn
        self.channel = channel
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.worker_count = worker_count
        self.workers = []
        self.listener_task = None
        self.db_pool = None
        self.shutdown_event = asyncio.Event()

    # START
    async def start(self):
        # Crear pool de DB
        self.db_pool = await asyncpg.create_pool(dsn=self.db_dsn)
        print(f"DB pool created for channel '{self.channel}' with {self.worker_count} workers.")

        # Lanzar listener async
        self.listener_task = asyncio.create_task(self._listener_loop())

        # Lanzar workers async
        for _ in range(self.worker_count):
            worker_task = asyncio.create_task(self._worker_loop())
            self.workers.append(worker_task)

        print("AsyncAlertManager started.")

    # LISTENER LOOP (PostgreSQL NOTIFY)
    async def _listener_loop(self):
        while not self.shutdown_event.is_set():
            try:
                async with self.db_pool.acquire() as conn:
                    # Escuchar canal de alertas
                    await conn.add_listener(self.channel, self._notify_callback)
                    while not self.shutdown_event.is_set():
                        await asyncio.sleep(1)  # mantener loop activo
            except Exception as e:
                print("Listener error:", e)
                await asyncio.sleep(2)  # reconexión lenta

    # CALLBACK por cada notificación
    def _notify_callback(self, connection, pid, channel, payload):
        try:
            event = json.loads(payload)
            if not self._validate_alert(event):
                print("Invalid alert, skipping:", event)
                return
            # Encolar evento sin bloquear
            asyncio.create_task(self.queue.put(event))
        except json.JSONDecodeError:
            print("Invalid JSON payload:", payload)

    # WORKER LOOP (async)
    async def _worker_loop(self):
        while not self.shutdown_event.is_set() or not self.queue.empty():
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=1)
                await self._process_alert(event)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print("Worker error:", e)

    # Procesamiento de alertas
    async def _process_alert(self, event):
        try:
            # Solo alertas críticas
            if event.get("severity") in ("error", "fatal"):
                async with self.db_pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(
                            "INSERT INTO alerts (id, severity, resource, payload) VALUES ($1, $2, $3, $4)",
                            event["id"], event["severity"], event["resource"], json.dumps(event)
                        )
                print(f"ALERT: {event['id']} - {event['severity']} on {event['resource']}")
        except Exception as e:
            print(f"DB write failed for alert {event.get('id')}: {e}")

    # Validación mínima
    def _validate_alert(self, event):
        return all(field in event for field in REQUIRED_ALERT_FIELDS)

    # GRACEFUL SHUTDOWN
    async def stop(self):
        print("AlertManager stopping...")
        self.shutdown_event.set()

        # Esperar que la cola se drene
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
        print("AlertManager stopped gracefully.")

async def main():
    alert_manager = AsyncAlertManager(db_dsn="postgres://user:pass@localhost/db", worker_count=2)
    await alert_manager.start()

    # Manejar SIGINT/SIGTERM para shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
    await stop_event.wait()
    await alert_manager.stop()
if __name__ == "__main__":
    asyncio.run(main())
