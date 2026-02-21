import unittest
from processor.main import Processor

class TestProcessor(unittest.TestCase):
    def test_validate_event(self):
        processor = Processor()
        valid_event = {"id": "1", "app_name": "App", "type": "T", "payload": {}}
        invalid_event = {"id": "2", "app_name": "App"}  # missing 'type'
        
        self.assertTrue(processor._validate_event(valid_event))
        self.assertFalse(processor._validate_event(invalid_event))

if __name__ == "__main__":
    unittest.main()

