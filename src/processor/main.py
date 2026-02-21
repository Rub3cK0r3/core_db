import json
import select
import threading
import queue
import time
from core.db.db_connection import DBConnection

# Configuración mínima de validación
REQUIRED_EVENT_FIELDS = ["id", "app_name", "type", "payload"]

class Processor:
    def __init__(self, max_queue_size=1000, worker_count=4):
        self.db_connection = DBConnection()  # Para listener thread
        self.conn = self.db_connection.conn
        self.running = False

        # Cola de eventos
        self.event_queue = queue.Queue(maxsize=max_queue_size)
        self.worker_threads = []
        self.worker_count = worker_count

        self.shutdown_event = threading.Event()
        self.listener_thread = None

    # =========================
    # START
    # =========================
    def start(self):
        self.running = True

        # Thread de escucha de NOTIFY
        self.listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True
        )
        self.listener_thread.start()

        # Threads que procesan eventos de la cola
        for _ in range(self.worker_count):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.worker_threads.append(t)

        print(f"Processor started with {self.worker_count} worker(s).")

    # =========================
    # LISTEN LOOP
    # =========================
    def _listen_loop(self):
        while self.running:
            try:
                rlist, _, _ = select.select([self.conn], [], [], 5)
                if not rlist:
                    continue

                self.conn.poll()

                # Encolar todos los eventos NOTIFY
                for notify in self.conn.notifies:
                    try:
                        event = json.loads(notify.payload)

                        if not self._validate_event(event):
                            print("Invalid event, skipping:", event)
                            continue

                        self.event_queue.put_nowait(event)

                    except json.JSONDecodeError:
                        print("Invalid JSON payload:", notify.payload)
                    except queue.Full:
                        print("Queue full, dropping event")

                self.conn.notifies.clear()

            except Exception as e:
                print("Processor listener error:", e)
                self._reconnect()

    # =========================
    # WORKER LOOP
    # =========================
    def _worker_loop(self):
        # Cada worker crea su propia conexión DB
        worker_db = DBConnection()
        conn = worker_db.conn

        while not self.shutdown_event.is_set() or not self.event_queue.empty():
            try:
                event = self.event_queue.get(timeout=1)
                self._process_event_db(event, worker_db)
                self.event_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print("Worker error:", e)

        worker_db.close()
        print("Worker thread exiting.")

    # =========================
    # Procesamiento de eventos con transacción
    # =========================
    def _process_event_db(self, event, db_instance):
        try:
            with db_instance.conn:  # Maneja commit/rollback automático
                cursor = db_instance.conn.cursor()
                cursor.execute(
                    "INSERT INTO events (id, app_name, type, payload) VALUES (%s, %s, %s, %s)",
                    (event["id"], event["app_name"], event["type"], json.dumps(event["payload"]))
                )
                cursor.close()
            print("Processed event:", event["id"])

        except Exception as e:
            print(f"DB write failed for event {event.get('id')}: {e}")

    # =========================
    # Validación mínima
    # =========================
    def _validate_event(self, event):
        return all(field in event for field in REQUIRED_EVENT_FIELDS)

    # =========================
    # Reconexión
    # =========================
    def _reconnect(self):
        print("Attempting reconnection...")
        time.sleep(2)
        try:
            self.db_connection.connect()
            self.conn = self.db_connection.conn
            print("Reconnected successfully.")
        except Exception as e:
            print("Reconnect failed:", e)

    # =========================
    # GRACEFUL SHUTDOWN
    # =========================
    def stop(self):
        print("Processor stopping...")
        self.running = False
        self.shutdown_event.set()

        if self.listener_thread:
            self.listener_thread.join(timeout=2)

        self.event_queue.join()

        for t in self.worker_threads:
            t.join(timeout=2)

        self.db_connection.close()
        print("Processor stopped gracefully.")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    processor = Processor(worker_count=4)
    processor.start()

    try:
        while True:
            cmd = input("Type 'quit' to stop: ")
            if cmd.strip().lower() == "quit":
                processor.stop()
                break
    except KeyboardInterrupt:
        processor.stop()

