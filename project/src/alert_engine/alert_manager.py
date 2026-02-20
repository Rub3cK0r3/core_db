import os
import psycopg2
import json
import select
from urllib.parse import quote_plus

class AlertManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "db"),
            database=os.environ.get("POSTGRES_DB", "coredb"),
            user=os.environ.get("POSTGRES_USER", "devuser"),
            password=quote_plus(os.environ.get("POSTGRES_PASSWORD", "devpass"))
        )
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.conn.cursor()
        self.cur.execute("LISTEN canal_eventos;")

    def start(self):
        print("AlertManager listening on canal_eventos...")
        while True:
            if select.select([self.conn], [], [], 5) == ([], [], []):
                continue
            self.conn.poll()
            while self.conn.notifies:
                notify = self.conn.notifies.pop(0)
                self.process_event(json.loads(notify.payload))

    def process_event(self, event):
        # Ejemplo simple: alertar si severity es error o fatal
        if event.get("severity") in ("error", "fatal"):
            print(f"ALERT: {event.get('id')} - {event.get('severity')} on {event.get('resource')}")

if __name__ == "__main__":
    am = AlertManager()
    am.start()

