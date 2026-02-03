import logging
import os
from logging.handlers import RotatingFileHandler

DEFAULT_LOGGER_NAME = "job_tracker"
DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DEFAULT_LOG_FILE = os.getenv("LOG_FILE")


def get_logger(name: str | None = None) -> logging.Logger:
    logger_name = name or DEFAULT_LOGGER_NAME
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(DEFAULT_LEVEL)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if DEFAULT_LOG_FILE:
        file_handler = RotatingFileHandler(
            DEFAULT_LOG_FILE,
            maxBytes=1_000_000,
            backupCount=3,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
