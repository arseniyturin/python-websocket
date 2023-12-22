import sys
import logging
import traceback
from logging.config import dictConfig


def get_logger(name: str):
    """
    Create logger. Name has options: __name__, "console" or "console_and_file"
    """
    config = {
        "version": 1,
        "formatters": {
            "console": {
                "format": "%(asctime)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": logging.INFO,
                "formatter": "console",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "console",
                "filename": "wsserver.log",
                "maxBytes": 1024,
            },
        },
        "loggers": {
            "__main__": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "console": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "console_and_file": {
                "handlers": ["console", "file"],
                "level": "INFO",
            },
        },
    }

    dictConfig(config)
    logger = logging.getLogger(name)

    def capture_uncaught_exception(t, v, tb):
        full_traceback = "\r\nTraceback (most recent call last):\n"
        full_traceback += "".join(traceback.format_tb(tb, None))
        logger.error(f"{t.__name__}: {v}{full_traceback}")

    sys.excepthook = capture_uncaught_exception

    return logger
