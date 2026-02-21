import time
import uuid
import random
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector.main import Collector
from processor.main import Processor
from alert_engine.main import AlertManager

NUM_EVENTS = 5000         # total eventos a generar
NUM_ALERTS = 500          # total alertas críticas
WORKER_COUNT = 4           # threads de Processor
ALERT_WORKERS = 2          # threads de AlertManager

APP_NAMES = ["Pizzeria Frontend", "Pizzeria Backend", "Pizzeria Mobile"]
SEVERITIES = ["debug", "info", "warning", "error", "fatal"]
APP_STAGES = ["development", "testing", "staging", "production"]

def generate_event(i):
    return {
        "id": f"evt-{uuid.uuid4()}",
        "severity": random.choice(SEVERITIES),
        "stack": "ReferenceError: x is not defined" if random.random() < 0.1 else None,
        "type": random.choice(["ReferenceError", "TypeError", "NetworkError", "Heartbeat", "DebugInfo"]),
        "timestamp": int(time.time() * 1000),
        "received_at": int(time.time() * 1000),
        "resource": f"/endpoint/{i % 10}",
        "referrer": f"https://example.com/page{i % 10}",
        "app_name": random.choice(APP_NAMES),
        "app_version": f"{random.randint(1,5)}.{random.randint(0,10)}.{random.randint(0,20)}",
        "app_stage": random.choice(APP_STAGES),
        "tags": {"env": "load-test"},
        "endpoint_id": str(uuid.uuid4()),
        "endpoint_language": "en-US",
        "endpoint_platform": random.choice(["MacIntel", "Linux x86_64", "iPhone", "Windows NT"]),
        "endpoint_os": random.choice(["MacOS", "Ubuntu", "iOS", "Windows"]),
        "endpoint_os_version": "1.0",
        "endpoint_runtime": "NodeJs",
        "endpoint_runtime_version": "18.15.0",
        "endpoint_country": random.choice(["US","GB","FR","ES"]),
        "endpoint_user_agent": "MockAgent/1.0",
        "endpoint_device_type": random.choice(["Desktop","Mobile"])
    }

def generate_alert(i):
    return {
        "id": f"alert-{uuid.uuid4()}",
        "severity": random.choice(["error","fatal"]),
        "resource": f"/alert/{i % 5}",
        "timestamp": int(time.time() * 1000),
        "received_at": int(time.time() * 1000),
        "app_name": random.choice(APP_NAMES),
        "endpoint_id": str(uuid.uuid4())
    }

if __name__ == "__main__":
    print("=== Starting Load Simulation ===")

    collector = Collector(max_queue_size=NUM_EVENTS)
    processor = Processor(worker_count=WORKER_COUNT)
    alert_manager = AlertManager(worker_count=ALERT_WORKERS)

    collector.start()
    processor.start()
    alert_manager.start()

    print(f"Generating {NUM_EVENTS} mock events...")
    for i in range(NUM_EVENTS):
        event = generate_event(i)
        try:
            collector.event_queue.put_nowait(event)
        except Exception:
            print("Collector queue full, dropping event")

    print(f"Generating {NUM_ALERTS} mock alerts...")
    for i in range(NUM_ALERTS):
        alert = generate_alert(i)
        try:
            alert_manager.event_queue.put_nowait(alert)
        except Exception:
            print("Alert queue full, dropping alert")

    print("Waiting for queues to drain...")
    collector.event_queue.join()
    alert_manager.event_queue.join()

    processor.stop()
    alert_manager.stop()
    collector.stop()

    print("=== Load Simulation completed successfully! ===")

