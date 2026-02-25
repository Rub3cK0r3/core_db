import asyncio
import asyncpg
import json
import signal

from core.async.async_manager import AsyncManager


REQUIRED_EVENT_FIELDS = ["type", "payload"]


class AsyncCollector:
    """ 
    Manages asynchronous collection of events from PostgreSQL
    and delegates processing to an AsyncManager.

    Works using:
    - A PostgreSQL listener that subscribes to the 'events_channel'.
    - An AsyncManager instance responsible for queueing and worker execution.
    - A processing coroutine that inserts validated events into the database.

    Attributes:
        db_dsn (str): Database connection string (PostgreSQL DSN).
        db_pool (asyncpg.pool.Pool): Connection pool to PostgreSQL.
        listener_task (asyncio.Task): Task running the event listener.
        async_manager (AsyncManager): Infrastructure component managing workers.
    """ 

    def __init__(self, db_dsn, worker_count=4, max_queue_size=1000):

        # Guardamos la cadena de conexión a la base de datos (db_dsn)
        # para poder crear posteriormente un pool de conexiones asíncrono
        self.db_dsn = db_dsn

        self.db_pool = None
        self.listener_task = None

        # Infraestructura async desacoplada
        self.async_manager = AsyncManager(
            worker_count=worker_count,
            max_queue_size=max_queue_size
        )

    # START
    async def start(self):
        """
        Initializes the AsyncCollector:
            - Creates the database connection pool.
            - Starts AsyncManager workers.
            - Launches the asynchronous listener for 'events_channel'.
        """

        # Crear pool de DB
        self.db_pool = await asyncpg.create_pool(dsn=self.db_dsn)
        print("DB pool created.")

        # Iniciar infraestructura async (workers)
        await self.async_manager.start(self._process_event_db)

        # Lanzar listener async
        self.listener_task = asyncio.create_task(self._listener_loop())

        print("AsyncCollector started.")

    # LISTENER LOOP (PostgreSQL NOTIFY)
    async def _listener_loop(self):
        """
        Asynchronous loop that keeps the PostgreSQL listener active.
            Connects to the 'events_channel' and registers `_notify_callback`
            for each incoming notification. Handles retries in case of errors.
        """
        while not self.async_manager.shutdown_event.is_set():
            try:
                async with self.db_pool.acquire() as conn:
                    # Escuchar canal 'events_channel'
                    await conn.add_listener("events_channel", self._notify_callback)

                    while not self.async_manager.shutdown_event.is_set():
                        await asyncio.sleep(1)  # Mantener el loop vivo

            except Exception as e:
                print("Listener error:", e)
                await asyncio.sleep(2)  # Retry lento

    # CALLBACK por cada notificación
    def _notify_callback(self, connection, pid, channel, payload):
        """
        Callback triggered by PostgreSQL NOTIFY events.

        Parses the JSON payload, validates the event, and enqueues it
        for asynchronous processing via AsyncManager.

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

            # Delegar en AsyncManager sin bloquear el callback
            asyncio.create_task(self.async_manager.enqueue(event))

        except json.JSONDecodeError:
            print("Invalid JSON payload:", payload)

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
                        event["type"],
                        json.dumps(event["payload"])
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
            - Stops the PostgreSQL listener.
            - Drains AsyncManager queue.
            - Stops worker tasks.
            - Closes the database connection pool.
        """ 
        print("Collector stopping...")

        # Stop async infrastructure first (drains queue)
        await self.async_manager.stop()

        # Cancel listener
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        # Close DB pool
        await self.db_pool.close()

        print("Collector stopped gracefully.")


async def main():
    """
    Example entry point for running the AsyncCollector.
        - Initializes the collector with PostgreSQL DSN and worker count.
        - Starts the collector.
        - Handles SIGINT/SIGTERM signals for graceful shutdown.
    """
    collector = AsyncCollector(
        db_dsn="postgres://user:pass@localhost/db",  # CAMBIAR POR LOS DEL ENTORNO
        worker_count=4
    )

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

