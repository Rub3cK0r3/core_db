import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from core.async_lib.async_manager import AsyncManager
from core.async_lib.processor.main import EventProcessor
from core.async_lib.alert_engine.main import AlertManager as AsyncAlertManager


class TestAsyncPipelineIntegration(unittest.TestCase):
    """
    End-to-end integration test for async pipeline:
    AsyncManager -> EventProcessor / AsyncAlertManager

    Verifies that events and alerts traverse the async queue
    and trigger API calls (mocked HTTP clients).
    """

    # Helper to run async coroutines in sync context
    def _run(self, coro):
        return asyncio.run(coro)

    @patch("core.async_lib.processor.main.httpx.AsyncClient")
    @patch("core.async_lib.alert_engine.main.httpx.AsyncClient")
    def test_events_and_alerts_flow_through_pipeline(self, mock_alert_client_cls, mock_event_client_cls):
        # -----------------------------
        # Mock HTTP client for events
        # -----------------------------
        mock_event_client = AsyncMock()
        event_cm = AsyncMock()
        event_cm.__aenter__.return_value = mock_event_client
        event_cm.__aexit__.return_value = None
        mock_event_client_cls.return_value = event_cm

        event_response = MagicMock()
        event_response.status_code = 200
        event_response.raise_for_status = MagicMock()  # sync method
        mock_event_client.post = AsyncMock(return_value=event_response)

        # -----------------------------
        # Mock HTTP client for alerts
        # -----------------------------
        mock_alert_client = AsyncMock()
        alert_cm = AsyncMock()
        alert_cm.__aenter__.return_value = mock_alert_client
        alert_cm.__aexit__.return_value = None
        mock_alert_client_cls.return_value = alert_cm

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

            # Instantiate AsyncAlertManager AFTER mocks are set
            alert_manager = AsyncAlertManager()

            # Start event workers
            await manager.start(processor.handle)

            # Enqueue events
            events = [
                {"id": f"evt-{i}", "app_name": "App", "type": "T", "payload": {"i": i}}
                for i in range(5)
            ]
            for e in events:
                await manager.enqueue(e)

            # Process alerts directly (not through the queue)
            alerts = [
                {"id": f"alert-{i}", "severity": "fatal", "resource": "res"}
                for i in range(3)
            ]
            for a in alerts:
                await alert_manager.handle(a)

            # Let async workers drain the queue
            await asyncio.sleep(0.1)

            # Stop workers gracefully
            await manager.stop()

        # Run the async scenario
        self._run(scenario())

        # -----------------------------
        # Assertions
        # -----------------------------
        # All events should trigger API calls
        self.assertGreaterEqual(mock_event_client.post.call_count, 5)
        # All fatal alerts should trigger API calls
        self.assertEqual(mock_alert_client.post.call_count, 3)


if __name__ == "__main__":
    unittest.main()
