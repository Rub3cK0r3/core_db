import asyncio
import asyncpg
import json
import signal

REQUIRED_EVENT_FIELDS = ["type", "payload"]

class AsyncCollector:
    """ 
    Manages asynchronous collection and processing of events from PostgreSQL.

    Works using:
    - A listener that subscribes to the 'events_channel' notifications.
    - An asyncio queue to store incoming events.
    - Asynchronous workers that process events and insert them into the database.

    Attributes:
        db_dsn (str): Database connection string (PostgreSQL DSN).
        queue (asyncio.Queue): Queue to store incoming events.
        worker_count (int): Number of concurrent workers processing events.
        workers (list): List of active worker tasks.
        listener_task (asyncio.Task): Task running the event listener.
        db_pool (asyncpg.pool.Pool): Connection pool to PostgreSQL.
        shutdown_event (asyncio.Event): Event to signal graceful shutdown.
    """ 
    def __init__(self, db_dsn, max_queue_size=1000, worker_count=4):
        
        # Guardamos la cadena de conexión a la base de datos (db_dsn)
        # para poder crear posteriormente un pool de conexiones asíncrono
        self.db_dsn = db_dsn
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        
        self.worker_count = worker_count
        
        self.workers = []
        
        self.listener_task = None
        self.db_pool = None
        
        self.shutdown_event = asyncio.Event()

    # START
    async def start(self):
        """
        Initializes the AsyncCollector:
            - Creates the database connection pool. 
            - Launches the asynchronous listener for 'events_channel'.
            - Starts workers that process events from the queue.
        """
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

    # LISTENER LOOP (PostgreSQL NOTIFY)
    async def _listener_loop(self):
        """
        Asynchronous loop that keeps the PostgreSQL listener active.
            Connects to the 'events_channel' and registers `_notify_callback` for
            each incoming notification. Handles retries in case of errors.
        """
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

    # CALLBACK por cada notificación
    def _notify_callback(self, connection, pid, channel, payload):
        """
        Callback triggered by PostgreSQL NOTIFY events.
        Parses the JSON payload, validates the event, and enqueues it for processing.
            Args:
                - connection: PostgreSQL connection that received the notification.
                - pid (int): Backend PID that sent the notification. 
                - channel (str): Name of the channel that sent the notification.
                - payload (str): Received JSON message.
        """
        try:
            event = json.loads(payload)
            if not self._validate_event(event):
                print("Invalid event, skipping:", event)
                return
            # Poner en la cola async sin bloquear
            asyncio.create_task(self.queue.put(event))
        except json.JSONDecodeError:
            print("Invalid JSON payload:", payload)

    # WORKER LOOP (async)
    async def _worker_loop(self):
        """
        Asynchronous loop of a worker that processes events from the queue.
            Retrieves events from `self.queue`, processes them with `_process_event_db`, 
            and marks the task as done.
        """
        while not self.shutdown_event.is_set() or not self.queue.empty():
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=1)
                await self._process_event_db(event)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print("Worker error:", e)

    # Procesamiento con transacción
    async def _process_event_db(self, event):
        """ 
        Inserts an event into the 'events' table in the database within a transaction.
        Args:
            event (dict): Event dictionary containing 'type' and 'payload' keys.
        """
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

    # Validación mínima
    def _validate_event(self, event):
        """ 
        Validates that an event contains all required fields.
        Args:
            event (dict): Event to validate.
        Returns:
            bool: True if all required fields are present, False otherwise.
        """
        return all(field in event for field in REQUIRED_EVENT_FIELDS)

    # GRACEFUL SHUTDOWN
    async def stop(self):
        """
        Performs a graceful shutdown of the AsyncCollector:
            - Signals listener and worker loops to stop.
            - Waits for the queue to drain.
            - Cancels listener and worker tasks.
            - Closes the database connection pool.
        """ 
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

async def main():
    """
    Example entry point for running the AsyncCollector.
        - Initializes the collector with PostgreSQL DSN and worker count.
        - Starts the collector.
        - Handles SIGINT/SIGTERM signals for graceful shutdown.
    """
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
