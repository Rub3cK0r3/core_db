import asyncio
import asyncpg
import json
import signal

# =========================
# Configuración mínima
# =========================
REQUIRED_EVENT_FIELDS = ["id", "app_name", "type", "payload"]
REQUIRED_ALERT_FIELDS = ["id", "severity", "resource"]

# =========================
# PIPELINE CLASE BASE
# =========================
class AsyncPipeline:
    def __init__(self, db_dsn, worker_count=4):
        self.db_dsn = db_dsn
        self.worker_count = worker_count
        self.shutdown_event = asyncio.Event()
        self.db_pool = None

        # Queues
        self.event_queue = asyncio.Queue(maxsize=1000)
        self.alert_queue = asyncio.Queue(maxsize=500)

        # Tareas
        self.listener_task = None
        self.worker_tasks = []
        self.alert_worker_tasks = []

    # =========================
    # START
    # =========================
    async def start(self):
        # Crear pool DB
        self.db_pool = await asyncpg.create_pool(dsn=self.db_dsn)
        print(f"DB pool created with {self.worker_count} workers")

        # Iniciar listener
        self.listener_task = asyncio.create_task(self._collector_listener())

        # Iniciar workers
        for _ in range(self.worker_count):
            self.worker_tasks.append(asyncio.create_task(self._processor_worker()))
        for _ in range(2):  # alert workers
            self.alert_worker_tasks.append(asyncio.create_task(self._alert_worker()))

        print("Pipeline started.")

    # =========================
    # LISTENER (Collector)
    # =========================
    async def _collector_listener(self):
        while not self.shutdown_event.is_set():
            try:
                async with self.db_pool.acquire() as conn:
                    # Escuchar canal principal de eventos
                    await conn.add_listener("events_channel", self._notify_callback)
                    while not self.shutdown_event.is_set():
                        await asyncio.sleep(1)  # mantener loop activo
            except Exception as e:
                print("Collector listener error:", e)
                await asyncio.sleep(2)

    # Callback de NOTIFY
    def _notify_callback(self, connection, pid, channel, payload):
        try:
            event = json.loads(payload)
            if self._validate_event(event):
                asyncio.create_task(self.event_queue.put(event))
        except json.JSONDecodeError:
            print("Invalid JSON payload:", payload)

    # =========================
    # PROCESSOR WORKER
    # =========================
    async def _processor_worker(self):
        while not self.shutdown_event.is_set() or not self.event_queue.empty():
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1)
                # Normalización / enriquecimiento
                event["processed"] = True

                # Insert DB
                await self._insert_event(event)

                # Si cumple criterios de alerta, enviar a alert_queue
                if event.get("type") in ("error", "critical"):
                    await self.alert_queue.put(event)

                self.event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print("Processor worker error:", e)

    async def _insert_event(self, event):
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        "INSERT INTO events(id, app_name, type, payload) VALUES($1,$2,$3,$4)",
                        event["id"], event["app_name"], event["type"], json.dumps(event)
                    )
            print(f"Processed event {event['id']}")
        except Exception as e:
            print(f"DB write failed for event {event.get('id')}: {e}")

    # =========================
    # ALERT WORKER
    # =========================
    async def _alert_worker(self):
        while not self.shutdown_event.is_set() or not self.alert_queue.empty():
            try:
                alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1)
                if self._validate_alert(alert):
                    await self._process_alert(alert)
                self.alert_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print("Alert worker error:", e)

    async def _process_alert(self, alert):
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        "INSERT INTO alerts(id,severity,resource,payload) VALUES($1,$2,$3,$4)",
                        alert["id"], alert.get("type"), alert.get("app_name"), json.dumps(alert)
                    )
            print(f"ALERT processed: {alert['id']}")
        except Exception as e:
            print(f"DB write failed for alert {alert.get('id')}: {e}")

    # =========================
    # VALIDACIONES
    # =========================
    def _validate_event(self, event):
        return all(field in event for field in REQUIRED_EVENT_FIELDS)

    def _validate_alert(self, event):
        return all(field in event for field in REQUIRED_ALERT_FIELDS)

    # =========================
    # GRACEFUL SHUTDOWN
    # =========================
    async def stop(self):
        print("Pipeline stopping...")
        self.shutdown_event.set()

        # Drenar colas
        await self.event_queue.join()
        await self.alert_queue.join()

        # Cancelar listener
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        # Cancelar workers
        for t in self.worker_tasks + self.alert_worker_tasks:
            t.cancel()
        await asyncio.gather(*(self.worker_tasks + self.alert_worker_tasks), return_exceptions=True)

        # Cerrar DB pool
        await self.db_pool.close()
        print("Pipeline stopped gracefully.")


# =========================
# MAIN
# =========================
async def main():
    pipeline = AsyncPipeline(db_dsn="postgres://user:pass@localhost/db", worker_count=4)
    await pipeline.start()

    # Manejar SIGINT/SIGTERM
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    await pipeline.stop()

if __name__ == "__main__":
    asyncio.run(main())

