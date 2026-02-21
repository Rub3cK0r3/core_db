import unittest
import threading
import time
import os,sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')

from collector.main import Collector
from processor.main import Processor
from alert_engine.main import AlertManager

class TestIntegration(unittest.TestCase):
    def test_pipeline(self):
        collector = Collector(max_queue_size=10)
        processor = Processor(worker_count=2)
        alert_manager = AlertManager(worker_count=1)
        
        # Mock events y alertas
        events = [{"id": i, "app_name": "App", "type": "T"} for i in range(5)]
        alerts = [{"id": i, "severity": "fatal", "resource": "res"} for i in range(3)]
        
        for e in events:
            collector.event_queue.put(e)
        for a in alerts:
            alert_manager.event_queue.put(a)
        
        t1 = threading.Thread(target=processor._worker_loop)
        t2 = threading.Thread(target=alert_manager._worker_loop)
        t1.start(); t2.start()
        
        time.sleep(2)
        
        self.assertTrue(collector.event_queue.empty())
        self.assertTrue(alert_manager.event_queue.empty())
        
        processor.stop()
        alert_manager.stop()
        t1.join(); t2.join()

if __name__ == "__main__":
    unittest.main()

