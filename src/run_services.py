import asyncio
from core.async_lib.collector.main import AsyncCollector
from core.async_lib.processor.main import EventProcessor
from core.async_lib.async_manager import AsyncManager
from core.backend.database import engine # or import your DB engine

async def start_services():
    processor = EventProcessor(engine)

    async_manager = AsyncManager(worker_count=4)
    await async_manager.start(processor.handle)

    collector = AsyncCollector(db_dsn=None, worker_count=4)
    collector.async_manager = async_manager
    collector.listener_task = asyncio.create_task(collector._listener_loop())

    print("All services started. Running forever...")

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        print("Stopping services...")
        collector.listener_task.cancel()
        try:
            await collector.listener_task
        except asyncio.CancelledError:
            pass
        await async_manager.stop()

def run_app():
    asyncio.run(start_services())

if __name__ == "__main__":
    run_app()

