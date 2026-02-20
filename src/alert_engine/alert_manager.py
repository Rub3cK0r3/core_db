import json
import select
from core.db.db_connection import DBConnection
class AlertManager:
    def __init__(self, channel: str = "canal_eventos"):
        # Use your DBConnection class
        self.db = DBConnection(channel=channel)
        self.conn = self.db.conn

    def start(self):
        print(f"AlertManager listening on channel '{self.db.channel}'...")
        while True:
            try:
                # Wait up to 5 seconds for DB notifications
                if select.select([self.conn], [], [], 5) == ([], [], []):
                    continue

                self.conn.poll()

                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    try:
                        event = json.loads(notify.payload)
                        self.process_event(event)
                    except json.JSONDecodeError:
                        print("Invalid payload:", notify.payload)

            except Exception as e:
                print("AlertManager error:", e)
                # Reconnect if connection is lost
                self.db.connect()
                self.conn = self.db.conn  # refresh reference

    def process_event(self, event: dict) -> None:
        # Example: alert if severity is error or fatal
        if event.get("severity") in ("error", "fatal"):
            print(
                f"ALERT: {event.get('id')} - {event.get('severity')} on {event.get('resource')}"
            )


if __name__ == "__main__":
    am = AlertManager()
    am.start()

