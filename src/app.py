import asyncio
from core.async.async_collector import AsyncCollector
from core.async.event_processor import EventProcessor
from core.async.alert_manager import AlertManager
from core.async.async_manager import AsyncManager
import asyncpg

async def start_services():
    # 1. DB pool
    db_pool = await asyncpg.create_pool("postgres://user:pass@localhost/db")

    # 2. Event Processor + Collector
    event_processor = EventProcessor(db_pool)
    event_async_manager = AsyncManager(worker_count=4)
    await event_async_manager.start(event_processor.handle)
    event_collector = AsyncCollector(
        db_dsn=None,  # pool already exists
        worker_count=4
    )
    event_collector.db_pool = db_pool
    event_collector.async_manager = event_async_manager
    event_collector.listener_task = asyncio.create_task(event_collector._listener_loop())

    # 3. Alert Manager + Collector
    alert_manager = AlertManager(db_pool)
    alert_async_manager = AsyncManager(worker_count=2)
    await alert_async_manager.start(alert_manager.handle)
    # You can create an AlertCollector similar to AsyncCollector
    # alert_collector.db_pool = db_pool
    # alert_collector.async_manager = alert_async_manager
    # alert_collector.listener_task = asyncio.create_task(alert_collector._listener_loop())

    print("All services started.")

    # Run forever, until cancelled
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        # Graceful shutdown
        print("Stopping services...")
        await event_collector.async_manager.stop()
        await alert_async_manager.stop()
        await db_pool.close()


# Entrypoint for any external script
def run_app():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_services())
    finally:
        loop.close()

