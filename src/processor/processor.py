# class to manage the processor implementation
import os
import psycopg2
import json
from urllib.parse import quote_plus
import select

class Processor:
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
        print("Processor listening...")
        while True:
            if select.select([self.conn], [], [], 5) == ([], [], []):
                continue
            self.conn.poll()
            while self.conn.notifies:
                notify = self.conn.notifies.pop(0)
                event = json.loads(notify.payload)
                self.process_event(event)

    def process_event(self, event):
        # Ejemplo: enriquecer y guardar en otra tabla
        print(f"Processing {event['id']} from {event.get('app_name')}")


if __name__ == "__main__":
    processor = Processor()
    processor.start()

