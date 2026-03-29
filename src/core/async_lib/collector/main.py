import asyncio
import json
import os
import signal

import asyncpg
import httpx

# Importar AsyncManager como antes
from core.async_lib.async_manager import AsyncManager

REQUIRED_EVENT_FIELDS = ["type", "payload"]

class AsyncCollector:
    def __init__(self, db_dsn, fastapi_app=None, worker_count=4, max_queue_size=1000, backend_base_url: str | None = None):

        self.db_dsn = db_dsn
        self.db_pool = None
        self.listener_task = None

        self.async_manager = AsyncManager(
            worker_count=worker_count,
            max_queue_size=max_queue_size
        )

        # Referencia a FastAPI (para WebSockets)
        self.fastapi_app = fastapi_app

        # Backend API base URL (para persistir eventos vía servicio)
        self.backend_base_url = backend_base_url or os.getenv("BACKEND_BASE_URL", "http://backend:8000")

    async def start(self):
        """Inicializa DB pool, workers y listener de eventos"""
        self.db_pool = await asyncpg.create_pool(dsn=self.db_dsn)
        print("DB pool created.")

        # Iniciar workers (procesan eventos)
        await self.async_manager.start(self._process_event)

        # Lanzar listener PostgreSQL
        self.listener_task = asyncio.create_task(self._listener_loop())
        print("AsyncCollector started.")

    async def _listener_loop(self):
        """Escucha canal 'events_channel' en PostgreSQL"""
        while not self.async_manager.shutdown_event.is_set():
            try:
                async with self.db_pool.acquire() as conn:
                    await conn.add_listener("events_channel", self._notify_callback)

                    while not self.async_manager.shutdown_event.is_set():
                        await asyncio.sleep(1)  # mantener loop vivo

            except Exception as e:
                print("Listener error:", e)
                await asyncio.sleep(2)  # retry lento

    def _notify_callback(self, connection, pid, channel, payload):
        """Se ejecuta al recibir NOTIFY desde PostgreSQL"""
        try:
            event = json.loads(payload)

            if not self._validate_event(event):
                print("Invalid event, skipping:", event)
                return

            # Encolamos el evento en AsyncManager
            asyncio.create_task(self.async_manager.enqueue(event))

        except json.JSONDecodeError:
            print("Invalid JSON payload:", payload)

    async def _process_event(self, event):
        """Procesa un evento: persiste vía API y notifica FastAPI WebSocket"""
        await self._insert_event_api(event)
        await self._notify_fastapi(event)

    async def _insert_event_api(self, event):
        try:
            async with httpx.AsyncClient(base_url=self.backend_base_url, timeout=5.0) as client:
                payload = {
                    "type": event["type"],
                    "payload": event,
                }
                response = await client.post("/internal/pipeline/events", json=payload)
                response.raise_for_status()

            print("Processed event via API:", event)

        except Exception as e:
            print("API write failed for event:", event, "Error:", e)

    async def _notify_fastapi(self, event):
        """Envia el evento a todos los WebSockets conectados en FastAPI"""
        if not self.fastapi_app:
            return

        # La app debe tener lista de conexiones: active_connections
        for ws in getattr(self.fastapi_app, "active_connections", []):
            try:
                await ws.send_json(event)
            except Exception as e:
                print("Error enviando evento a websocket:", e)

    def _validate_event(self, event):
        return all(field in event for field in REQUIRED_EVENT_FIELDS)

    async def stop(self):
        """Apaga listener, workers y DB pool"""
        print("Collector stopping...")

        # Detener workers
        await self.async_manager.stop()

        # Cancelar listener
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        # Cerrar pool DB
        await self.db_pool.close()
        print("Collector stopped gracefully.")


async def main():
    from fastapi import FastAPI

    app = FastAPI()
    app.active_connections = []  # lista de WebSockets para notificaciones

    db_dsn = os.getenv("DATABASE_URL", "postgresql://devuser:devpass@db:5432/eventdb")

    collector = AsyncCollector(
        db_dsn=db_dsn,
        fastapi_app=app,
        worker_count=4,
    )

    await collector.start()

    # Manejo de SIGINT/SIGTERM
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    await collector.stop()


if __name__ == "__main__":
    asyncio.run(main())

