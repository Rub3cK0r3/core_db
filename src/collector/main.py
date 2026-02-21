import json
import select
import threading
from core.db.db_connection import DBConnection
# Integrate observer core class
class Collector:
    def __init__(self):
        self.db = DBConnection()
        self.conn = self.db.conn
        self.running = False
        
    def start(self):
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        self.running = False
        print("Collector started in a separate thread.")
    
    def _listen_loop(self):
        while self.running:
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


    def stop(self):
        self.running = False
        print("Collector stopping...")

if __name__ == "__main__":
    collector = Collector()
    collector.start()

    try:
        while True:
            cmd = input("Type 'quit' to stop: ")
            if cmd.strip() == "quit":
                collector.stop()
                break
    except KeyboardInterrupt:
        collector.stop()

