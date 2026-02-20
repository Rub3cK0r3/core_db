# class to manage the processor implementation
import json
import select
from core.db.db_connection import DBConnection
class Processor:
    def __init__(self):
        self.db_connection = DBConnection()
        self.conn = self.db_connection.conn

    def start(self):
        print("Processor listening...")
        while True:
            try:
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
                print("Processor error:", e)
                self.db_connection.connect()
                self.conn = self.db_connection.conn

    def process_event(self, event: dict) -> None:
        print(f"Processing {event.get('id')} from {event.get('app_name')}")

