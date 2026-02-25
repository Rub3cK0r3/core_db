import asyncpg
import json

REQUIRED_EVENT_FIELDS = ["id", "app_name", "type", "payload"]


class EventProcessor:
    """
    Handles business logic for processing events asynchronously.

    Responsibilities:
        - Validate incoming events.
        - Persist valid events into the database.
        - Encapsulate database transaction logic.

    This class does NOT manage:
        - Async workers
        - Queues
        - PostgreSQL listeners
        - Application lifecycle
    """

    def __init__(self, db_pool: asyncpg.pool.Pool):
        """
        Initializes the EventProcessor.

        Args:
            db_pool (asyncpg.pool.Pool): Active PostgreSQL connection pool.
        """
        self.db_pool = db_pool

    # PUBLIC ENTRY POINT
    async def handle(self, event: dict):
        """
        Main processing entry point used by AsyncManager workers.

        Args:
            event (dict): Incoming event dictionary.
        """
        if not self._validate_event(event):
            print("Invalid event, skipping:", event)
            return

        await self._insert_event(event)

    # DATABASE INSERT
    async def _insert_event(self, event: dict):
        """
        Inserts an event into the 'events' table using a transaction.

        Args:
            event (dict): Event dictionary containing
                'id', 'app_name', 'type', and 'payload'.
        """
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        """
                        INSERT INTO events(id, app_name, type, payload)
                        VALUES($1, $2, $3, $4)
                        """,
                        event["id"],
                        event["app_name"],
                        event["type"],
                        json.dumps(event["payload"])
                    )

            print(f"Processed event: {event['id']}")

        except Exception as e:
            print(f"DB write failed for event {event.get('id')}: {e}")

    # VALIDATION
    def _validate_event(self, event: dict) -> bool:
        """
        Validates that an event contains all required fields.

        Args:
            event (dict): Event to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return all(field in event for field in REQUIRED_EVENT_FIELDS)

