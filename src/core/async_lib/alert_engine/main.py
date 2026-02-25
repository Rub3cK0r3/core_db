import asyncio
import asyncpg
import json

from core.async_lib.async_manager import AsyncManager

REQUIRED_ALERT_FIELDS = ["id", "severity", "resource"]


class AlertManager:
    """
    Handles asynchronous processing of alert events.

    Responsibilities:
        - Validate incoming alerts.
        - Persist critical alerts ('error' or 'fatal') into the database.

    This class does NOT manage:
        - Async workers
        - Queues
        - PostgreSQL listeners
        - Application lifecycle
    """

    def __init__(self, db_pool: asyncpg.pool.Pool):
        """
        Initializes the AlertManager.

        Args:
            db_pool (asyncpg.pool.Pool): Active PostgreSQL connection pool.
        """
        self.db_pool = db_pool

    # PUBLIC ENTRY POINT
    async def handle(self, alert: dict):
        """
        Main processing entry point used by AsyncManager workers.

        Args:
            alert (dict): Incoming alert dictionary.
        """
        if not self._validate_alert(alert):
            print("Invalid alert, skipping:", alert)
            return

        await self._process_alert(alert)

    # DATABASE INSERT
    async def _process_alert(self, alert: dict):
        """
        Processes an alert by storing critical alerts in the database.
        Only alerts with severity 'error' or 'fatal' are inserted into 'alerts'.

        Args:
            alert (dict): Alert dictionary containing 'id', 'severity', 'resource', and other fields.
        """
        try:
            if alert.get("severity") in ("error", "fatal"):
                async with self.db_pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(
                            "INSERT INTO alerts (id, severity, resource, payload) VALUES ($1, $2, $3, $4)",
                            alert["id"],
                            alert["severity"],
                            alert["resource"],
                            json.dumps(alert),
                        )
                print(f"ALERT: {alert['id']} - {alert['severity']} on {alert['resource']}")

        except Exception as e:
            print(f"DB write failed for alert {alert.get('id')}: {e}")

    # VALIDATION
    def _validate_alert(self, alert: dict) -> bool:
        """
        Validates that an alert contains all required fields.

        Args:
            alert (dict): Alert to validate.

        Returns:
            bool: True if all required fields are present, False otherwise.
        """
        return all(field in alert for field in REQUIRED_ALERT_FIELDS)

