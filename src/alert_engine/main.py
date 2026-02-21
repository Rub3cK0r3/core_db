import json
import select
import threading
import queue
import time
from core.db.db_connection import DBConnection

# Campos mínimos requeridos en alert
REQUIRED_ALERT_FIELDS = ["id", "severity", "resource"]

class AlertManager:
    def __init__(self, channel: str = "canal_eventos", max_queue_size=1000, worker_count=2):
        self.db = DBConnection(channel=channel)
        self.conn = self.db.conn
        self.channel = channel
        self.running = False

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

        # Thread de escucha
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()

        # Workers que procesan la cola
        for _ in range(self.worker_count):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.worker_threads.append(t)

        print(f"AlertManager started on channel '{self.channel}' with {self.worker_count} worker(s).")

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

                # Encolar todas las notificaciones
                for notify in self.conn.notifies:
                    try:
                        event = json.loads(notify.payload)

                        if not self._validate_alert(event):
                            print("Invalid alert, skipping:", event)
                            continue

                        self.event_queue.put_nowait(event)

                    except json.JSONDecodeError:
                        print("Invalid JSON payload:", notify.payload)
                    except queue.Full:
                        print("Queue full, dropping alert")

                self.conn.notifies.clear()

            except Exception as e:
                print("AlertManager listener error:", e)
                self._reconnect()

    # =========================
    # WORKER LOOP
    # =========================
    def _worker_loop(self):
        # Cada worker crea su propia conexión DB
        worker_db = DBConnection(channel=self.channel)
        conn = worker_db.conn

        while not self.shutdown_event.is_set() or not self.event_queue.empty():
            try:
                event = self.event_queue.get(timeout=1)
                self._process_alert(event, worker_db)
                self.event_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print("Worker error:", e)

        worker_db.close()
        print("Worker thread exiting.")

    # =========================
    # Procesamiento de alertas
    # =========================
    def _process_alert(self, event, db_instance):
        try:
            # Solo alertas críticas
            if event.get("severity") in ("error", "fatal"):
                with db_instance.conn:  # transacción segura
                    cursor = db_instance.conn.cursor()
                    cursor.execute(
                        "INSERT INTO alerts (id, severity, resource, payload) VALUES (%s, %s, %s, %s)",
                        (event["id"], event["severity"], event["resource"], json.dumps(event))
                    )
                    cursor.close()
                print(f"ALERT: {event['id']} - {event['severity']} on {event['resource']}")

        except Exception as e:
            print(f"DB write failed for alert {event.get('id')}: {e}")

    # =========================
    # Validación mínima
    # =========================
    def _validate_alert(self, event):
        return all(field in event for field in REQUIRED_ALERT_FIELDS)

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
        print("AlertManager stopping...")
        self.running = False
        self.shutdown_event.set()

        if self.listener_thread:
            self.listener_thread.join(timeout=2)

        # Drenar cola
        self.event_queue.join()

        # Esperar workers
        for t in self.worker_threads:
            t.join(timeout=2)

        self.db.close()
        print("AlertManager stopped gracefully.")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    am = AlertManager(worker_count=2)
    am.start()

    try:
        while True:
            cmd = input("Type 'quit' to stop: ")
            if cmd.strip().lower() == "quit":
                am.stop()
                break
    except KeyboardInterrupt:
        am.stop()

