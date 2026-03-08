import os

import asyncpg
import httpx

REQUIRED_ALERT_FIELDS = ["id", "severity", "resource"]


class AlertManager:
    """
    Handles asynchronous processing of alert events.

    Responsibilities:
        - Validate incoming alerts.
        - Persist critical alerts ('error' or 'fatal') via the backend API.

    This class does NOT manage:
        - Async workers
        - Queues
        - PostgreSQL listeners
        - Application lifecycle
    """

    def __init__(self, db_pool: asyncpg.pool.Pool | None = None, backend_base_url: str | None = None):
        """
        Initializes the AlertManager.

        Args:
            db_pool (asyncpg.pool.Pool | None): Kept for backwards compatibility but no longer used.
            backend_base_url (str | None): Base URL of the backend API.
        """
        self.db_pool = db_pool
        self.backend_base_url = backend_base_url or os.getenv("BACKEND_BASE_URL", "http://backend:8000")

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

    # API INSERT
    async def _process_alert(self, alert: dict):
        """
        Processes an alert by sending critical alerts to the backend API.
        Only alerts with severity 'error' or 'fatal' are sent.
        """
        try:
            if alert.get("severity") in ("error", "fatal"):
                async with httpx.AsyncClient(base_url=self.backend_base_url, timeout=5.0) as client:
                    payload = {
                        "id": alert["id"],
                        "severity": alert["severity"],
                        "resource": alert.get("resource"),
                        "payload": alert,
                    }
                    response = await client.post("/internal/pipeline/alerts", json=payload)
                    response.raise_for_status()

                print(f"ALERT via API: {alert['id']} - {alert['severity']} on {alert.get('resource')}")

        except Exception as e:
            print(f"API write failed for alert {alert.get('id')}: {e}")

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

