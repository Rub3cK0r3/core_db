import asyncio
import unittest
from unittest.mock import AsyncMock, patch

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
        # Configure HTTP client mocks
        mock_event_client = AsyncMock()
        mock_event_client.__aenter__.return_value = mock_event_client
        mock_event_client.post.return_value = AsyncMock(status_code=200)
        mock_event_client_cls.return_value = mock_event_client

        mock_alert_client = AsyncMock()
        mock_alert_client.__aenter__.return_value = mock_alert_client
        mock_alert_client.post.return_value = AsyncMock(status_code=200)
        mock_alert_client_cls.return_value = mock_alert_client

        async def scenario():
            manager = AsyncManager(worker_count=4, max_queue_size=100)
            processor = EventProcessor()
            alert_manager = AsyncAlertManager()

            # Start workers for events and alerts
            await manager.start(processor.handle)

            # Enqueue events
            events = [
                {"id": f"evt-{i}", "app_name": "App", "type": "T", "payload": {"i": i}}
                for i in range(5)
            ]
            for e in events:
                await manager.enqueue(e)

            # Process alerts directly through alert manager (no queue layer yet)
            alerts = [
                {"id": f"alert-{i}", "severity": "fatal", "resource": "res"}
                for i in range(3)
            ]
            for a in alerts:
                await alert_manager.handle(a)

            # Give the workers a moment to drain the queue
            await asyncio.sleep(0.1)

            await manager.stop()

        self._run(scenario())

        # All events should have triggered an API call
        self.assertGreaterEqual(mock_event_client.post.call_count, 5)
        # All fatal alerts should have triggered an API call
        self.assertEqual(mock_alert_client.post.call_count, 3)


if __name__ == "__main__":
    unittest.main()

