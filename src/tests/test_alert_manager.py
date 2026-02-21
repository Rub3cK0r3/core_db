import unittest
from alert_engine.main import AlertManager

class TestAlertManager(unittest.TestCase):
    def test_validate_alert(self):
        am = AlertManager()
        valid_alert = {"id": "1", "severity": "fatal", "resource": "res"}
        invalid_alert = {"id": "2", "severity": "info"}  # no crítico
        
        self.assertTrue(am._validate_alert(valid_alert))
        self.assertFalse(am._validate_alert(invalid_alert))

if __name__ == "__main__":
    unittest.main()

