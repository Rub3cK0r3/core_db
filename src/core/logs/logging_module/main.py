import logging
from typing import Optional
from rich.logging import RichHandler

MIN_LEVEL = logging.INFO

class Logger():
    def __init__(self,file : Optional[str] = None ) -> None: 
        self.logger = logging.getLogger("logger")
        self.logger.setLevel(MIN_LEVEL)
        self.logger.propagate = False # Avoid double logging if root logger exists.

        # Formatter in order to define the format of the output
        self.formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Prevent adding multiple handlers if instance already exists
        if not self.logger.handlers:
            console_handler = RichHandler()
            console_handler.setLevel(MIN_LEVEL)
            handlers = [console_handler]

            if file:
                file_handler = logging.FileHandler(file)
                file_handler.setLevel(MIN_LEVEL)
                handlers.append(file_handler)

            for handler in handlers:
                handler.setFormatter(self.formatter)
                self.logger.addHandler(handler)

    # Convenience methods
    def debug(self, msg: str):
            self.logger.debug(msg)

    def info(self, msg: str):
            self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)
 
    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)
