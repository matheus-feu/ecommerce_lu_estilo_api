import logging
import os
from logging.handlers import TimedRotatingFileHandler

from src.core.settings import settings


class Logger:
    @staticmethod
    def get_logger(filename: str = "", name: str = ""):
        # Get directory
        parent_directory = os.path.dirname(filename)
        parent_directory = os.path.join(settings.logs.LOGS_DIR, parent_directory)

        # Create directory if not exists
        if parent_directory and not os.path.exists(parent_directory):
            os.makedirs(parent_directory)

        log_file_name = os.path.join(
            parent_directory, os.path.basename(filename) + ".log"
        )
        logging_level = settings.logs.LOGGING_LEVEL
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logger = logging.getLogger(name)

        # Add Time Rotating File Handler
        handler = TimedRotatingFileHandler(
            filename=log_file_name, when="midnight", interval=1, backupCount=30
        )
        handler.suffix = "%Y-%m-%d"
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging_level)

        return logger


logger = Logger.get_logger(__name__)
