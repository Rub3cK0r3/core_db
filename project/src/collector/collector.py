# class to manage the collector implementation
# It behaves like a queue of operations to do related to the 
# db, think it throught

# It gets the entrances requests to the db and collect them in the process
# to pass them to the processor

# At the end of the day this is a traffic proxy db
import psycopg2
import os
import json
import select
import time
from urllib.parse import quote_plus

class Collector:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.connect()

    def connect(self):
        while True:
            try:
                self.conn = psycopg2.connect(
                    host=os.environ.get("DB_HOST", "db"),
                    database=os.environ.get("POSTGRES_DB", "coredb"),
                    user=os.environ.get("POSTGRES_USER", "devuser"),
                    password=quote_plus(os.environ.get("POSTGRES_PASSWORD", "devpass"))
                )
                self.conn.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
                )
                self.cur = self.conn.cursor()
                self.cur.execute("LISTEN canal_eventos;")
                break
            except Exception as e:
                print("Connection error:", e)
                time.sleep(5)

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
                self.connect()

    def process_event(self, event):
        print("Processing event:", event)


if __name__ == "__main__":
    collector = Collector()
    collector.start()
