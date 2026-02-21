import json
import select
import threading
from core.db.db_connection import DBConnection

class AlertManager:
    def __init__(self, channel: str = "canal_eventos"):
        self.db = DBConnection(channel=channel)
        self.conn = self.db.conn
        self.running = False  # Flag para controlar el thread

    def start(self):
        self.running = True
        # Inicia el listener en un thread separado
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        print(f"AlertManager listening on channel '{self.db.channel}' in a thread...")

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
                print("AlertManager error:", e)
                self.db.connect()
                self.conn = self.db.conn

    def process_event(self, event: dict) -> None:
        if event.get("severity") in ("error", "fatal"):
            print(
                f"ALERT: {event.get('id')} - {event.get('severity')} on {event.get('resource')}"
            )

    def stop(self):
        self.running = False
        print("AlertManager stopping...")

if __name__ == "__main__":
    am = AlertManager()
    am.start()

    try:
        while True:
            cmd = input("Type 'quit' to stop: ")
            if cmd.strip().lower() == "quit":
                am.stop()
                break
    except KeyboardInterrupt:
        am.stop()

