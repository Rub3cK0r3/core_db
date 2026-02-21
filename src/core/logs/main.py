class Observer:
    def __init__(self):
        self.handlers = []

    def register_handler(self, handler):
        self.handlers.append(handler)

    def notify(self, event):
        for handler in self.handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Handler error: {e}")
