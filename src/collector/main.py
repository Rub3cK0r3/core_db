import json
import select
import threading
import queue
import time
from core.db.db_connection import DBConnection

# =========================
# Configuración mínima de validación
# =========================
REQUIRED_EVENT_FIELDS = ["type", "payload"]

class Collector:
    def __init__(self, max_queue_size=1000, worker_count=4):
        self.db = DBConnection()  # para listener thread si es necesario
        self.conn = self.db.conn
        self.running = False

        self.event_queue = queue.Queue(maxsize=max_queue_size)
        self.listener_thread = None
        self.worker_threads = []
        self.worker_count = worker_count

        self.shutdown_event = threading.Event()

    # =========================
    # START
    # =========================
    def start(self):
        self.running = True

        # Thread de escucha
        self.listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True
        )
        self.listener_thread.start()

        # Worker threads
        for _ in range(self.worker_count):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.worker_threads.append(t)

        print(f"Collector started with {self.worker_count} worker(s).")

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

                for notify in self.conn.notifies:
                    try:
                        event = json.loads(notify.payload)

                        # Validación mínima
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
                print("Collector error:", e)
                self._reconnect()

    # =========================
    # WORKER LOOP (DB por thread)
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

        # Cerrar conexión cuando el worker termina
        worker_db.close()
        print("Worker thread exiting.")

    # =========================
    # Procesamiento con transacción
    # =========================
    def _process_event_db(self, event, db_instance):
        try:
            # Transacción explícita
            with db_instance.conn:
                cursor = db_instance.conn.cursor()
                # Ejemplo de query parametrizada
                cursor.execute(
                    "INSERT INTO events (type, payload) VALUES (%s, %s)",
                    (event["type"], json.dumps(event["payload"]))
                )
                cursor.close()
            print("Processed event:", event)

        except Exception as e:
            print("DB write failed for event:", event, "Error:", e)

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
            self.db.connect()
            self.conn = self.db.conn
            print("Reconnected successfully.")
        except Exception as e:
            print("Reconnect failed:", e)

    # =========================
    # GRACEFUL SHUTDOWN
    # =========================
    def stop(self):
        print("Collector stopping...")
        self.running = False
        self.shutdown_event.set()

        # Esperar a que listener termine
        if self.listener_thread:
            self.listener_thread.join(timeout=2)

        # Esperar que la cola se drene
        self.event_queue.join()

        # Esperar a que todos los workers terminen
        for t in self.worker_threads:
            t.join(timeout=2)

        # Cerrar DB principal
        self.db.close()
        print("Collector stopped gracefully.")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    collector = Collector(worker_count=4)
    collector.start()

    try:
        while True:
            cmd = input("Type 'quit' to stop: ")
            if cmd.strip().lower() == "quit":
                collector.stop()
                break
    except KeyboardInterrupt:
        collector.stop()

