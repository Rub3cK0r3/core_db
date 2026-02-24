import asyncio
import asyncpg
import json
import signal

REQUIRED_ALERT_FIELDS = ["id", "severity", "resource"]

class AsyncAlertManager:
    def __init__(self, db_dsn, channel="canal_eventos", max_queue_size=1000, worker_count=2):
        """
        Manages asynchronous collection and processing of alert events from PostgreSQL.

        Uses:
            - A listener that subscribes to a specific PostgreSQL notification channel.
            - An asyncio queue to store incoming alerts.
            - Asynchronous workers that process critical alerts and insert them into the database.

        Attributes:
            db_dsn (str): PostgreSQL database connection string (DSN).
            channel (str): PostgreSQL NOTIFY channel to listen to.
            queue (asyncio.Queue): Queue to store incoming alerts.
            worker_count (int): Number of concurrent workers processing alerts.
            workers (list): List of active worker tasks.
            listener_task (asyncio.Task): Task running the alert listener.
            db_pool (asyncpg.pool.Pool): Connection pool to PostgreSQL.
            shutdown_event (asyncio.Event): Event to signal graceful shutdown.
        """
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
        """
        Initializes the AsyncAlertManager:
            - Creates the database connection pool.
            - Starts the asynchronous listener for the configured channel.
            - Launches worker tasks that process alerts from the queue.
        """
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
        """
        Asynchronous loop that keeps the PostgreSQL listener active.
            Registers `_notify_callback` for each NOTIFY event received from the configured channel.
            Handles reconnection retries in case of listener errors.
        """
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
        """
            Callback triggered by PostgreSQL NOTIFY events.

            Parses the JSON payload, validates the alert, and enqueues it for processing.

            Args:
                connection: PostgreSQL connection that received the notification.
                pid (int): Backend PID that sent the notification.
                channel (str): Name of the channel that sent the notification.
                payload (str): Received JSON message.
        """
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
        """
        Asynchronous loop for a worker that processes alerts from the queue.
            Retrieves alerts from `self.queue`, processes critical alerts via `_process_alert`,
            and marks the queue task as done. Continues until shutdown event is set and queue is empty.
        """
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
        """
        Processes an alert event by storing critical alerts in the database.
        Only alerts with severity 'error' or 'fatal' are inserted into the 'alerts' table.
        Args:
            - event (dict): Alert dictionary containing 'id', 'severity', 'resource', and other fields.
        """
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
        """
        Validates that an alert contains all required fields.

        Args:
            event (dict): Alert to validate.

        Returns:
            bool: True if all required fields ('id', 'severity', 'resource') are present,
                False otherwise.
        """
        return all(field in event for field in REQUIRED_ALERT_FIELDS)

    # GRACEFUL SHUTDOWN
    async def stop(self):
        """
        Performs a graceful shutdown of the AsyncAlertManager:
            - Signals listener and worker loops to stop.
            - Waits for the queue to drain.
            - Cancels listener and worker tasks.
            - Closes the database connection pool.
        """ 
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
    """
    Example entry point for running the AsyncAlertManager.

    - Initializes the manager with PostgreSQL DSN, channel, and worker count.
    - Starts the manager.
    - Handles SIGINT/SIGTERM signals for graceful shutdown.
    """
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
