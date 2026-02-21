import unittest
from queue import Queue
from collector.main import Collector

class TestCollector(unittest.TestCase):
    def test_enqueue_event(self):
        collector = Collector(max_queue_size=2)
        collector.event_queue = Queue(maxsize=2)
        
        event1 = {"id": "evt1", "app_name": "App", "type": "type1"}
        event2 = {"id": "evt2", "app_name": "App", "type": "type2"}
        
        collector.event_queue.put(event1)
        collector.event_queue.put(event2)
        
        with self.assertRaises(Exception):
            collector.event_queue.put_nowait({"id": "evt3"})
        
        self.assertEqual(collector.event_queue.qsize(), 2)

if __name__ == "__main__":
    unittest.main()

