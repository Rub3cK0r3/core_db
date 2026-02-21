# class to manage the processor implementation
import json
import select
import threading
from core.db.db_connection import DBConnection

# Integrate the Observer here too.
class Processor:
    def __init__(self):
        self.db_connection = DBConnection()
        self.conn = self.db_connection.conn
        self.running = False  # Flag para controlar el thread

    def start(self):
        self.running = True
        # Inicia el listener en un thread separado
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        print("Processor listening in a thread...")

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
                print("Processor error:", e)
                self.db_connection.connect()
                self.conn = self.db_connection.conn

    def process_event(self, event: dict) -> None:
        # Just printing for now
        print(f"Processing {event.get('id')} from {event.get('app_name')}")

    def stop(self):
        self.running = False
        print("Processor stopping...")

if __name__ == "__main__":
    processor = Processor()
    processor.start()

    try:
        while True:
            cmd = input("Type 'quit' to stop: ")
            if cmd.strip().lower() == "quit":
                processor.stop()
                break
    except KeyboardInterrupt:
        processor.stop()

