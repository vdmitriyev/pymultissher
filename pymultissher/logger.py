import logging
import os
import sys
import time
import uuid
from datetime import datetime

from pymultissher.constants import LOG_FILE_NAME


def get_logger(logger_name: str = None, logging_level: int = None) -> None:
    """Gets a configured logger for the class

    Args:
        logging_level (int): level of the logging
    """

    # silence paramiko logging
    transport_logger = logging.getLogger("paramiko.transport")
    transport_logger.setLevel(logging.ERROR)

    # Sets up a logger that logs to both a file and the console.
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(LOG_FILE_NAME)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("pymultissher")

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

    if logging_level is not None:
        logger.setLevel(logging_level)

    return logger
