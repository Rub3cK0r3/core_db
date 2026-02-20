# class to manage the collector implementation
# It behaves like a queue of operations to do related to the 
# db, think it throught

# It gets the entrances requests to the db and collect them in the process
# to pass them to the processor

# At the end of the day this is a traffic proxy db
import json
import select
from core.db.db_connection import DBConnection

class Collector:
    def __init__(self):
        self.db = DBConnection()
        self.conn = self.db.conn

    def start(self):
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
                print("Collector error:", e)
                self.db.connect()
                self.conn = self.db.conn

    def process_event(self, event):
        print("Processing event:", event)


if __name__ == "__main__":
    collector = Collector()
    collector.start()
