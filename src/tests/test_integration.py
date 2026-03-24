import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from core.async_lib.async_manager import AsyncManager
from core.async_lib.processor.main import EventProcessor
from core.async_lib.alert_engine.main import AlertManager as AsyncAlertManager


class TestAsyncPipelineIntegration(unittest.TestCase):
    """
    Minimal end-to-end test for the async pipeline:
        AsyncManager -> EventProcessor / AlertManager

    It verifies that valid events and alerts traverse the queue and
    reach the backend API integration points (mocked).
    """

    def _run(self, coro):
        return asyncio.run(coro)

    @patch("core.async_lib.processor.main.httpx.AsyncClient")
    @patch("core.async_lib.alert_engine.main.httpx.AsyncClient")
    def test_events_and_alerts_flow_through_pipeline(self, mock_alert_client_cls, mock_event_client_cls):
        # -----------------------------
        # Configure EVENT HTTP client mock
        # -----------------------------
        mock_event_client = AsyncMock()
        mock_event_cm = AsyncMock()
        mock_event_cm.__aenter__.return_value = mock_event_client
        mock_event_cm.__aexit__.return_value = None
        mock_event_client_cls.return_value = mock_event_cm

        event_response = MagicMock()
        event_response.status_code = 200
        event_response.raise_for_status = MagicMock()
        mock_event_client.post = AsyncMock(return_value=event_response)

        # -----------------------------
        # Configure ALERT HTTP client mock
        # -----------------------------
        mock_alert_client = AsyncMock()
        mock_alert_cm = AsyncMock()
        mock_alert_cm.__aenter__.return_value = mock_alert_client
        mock_alert_cm.__aexit__.return_value = None
        mock_alert_client_cls.return_value = mock_alert_cm

        alert_response = MagicMock()
        alert_response.status_code = 200
        alert_response.raise_for_status = MagicMock()
        mock_alert_client.post = AsyncMock(return_value=alert_response)

        # -----------------------------
        # Scenario: enqueue events & alerts
        # -----------------------------
        async def scenario():
            manager = AsyncManager(worker_count=4, max_queue_size=100)
            processor = EventProcessor()

            # Create the alert manager AFTER mocks are set up
            alert_manager = AsyncAlertManager()

            # Start workers for event processing
            await manager.start(processor.handle)

            # Enqueue events
            events = [
                {"id": f"evt-{i}", "app_name": "App", "type": "T", "payload": {"i": i}}
                for i in range(5)
            ]
            for e in events:
                await manager.enqueue(e)

            # Process alerts directly (not via queue)
            alerts = [
                {"id": f"alert-{i}", "severity": "fatal", "resource": "res"}
                for i in range(3)
            ]
            for a in alerts:
                await alert_manager.handle(a)

            # Allow time for async workers to process the queue
            await asyncio.sleep(0.1)

            # Stop workers gracefully
            await manager.stop()

        # Run async scenario
        self._run(scenario())

        # -----------------------------
        # Assertions
        # -----------------------------
        self.assertGreaterEqual(mock_event_client.post.call_count, 5)
        self.assertEqual(mock_alert_client.post.call_count, 3)


if __name__ == "__main__":
    unittest.main()
