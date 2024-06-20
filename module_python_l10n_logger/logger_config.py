#!/opt/venv/bin/python3

# logger_config.py

import logging
import pytz
from datetime import datetime

class SydneyFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def converter(self, timestamp):
        return datetime.fromtimestamp(timestamp, pytz.timezone('Australia/Sydney'))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

def setup_logger(name, level=logging.INFO):
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create formatter
    formatter = SydneyFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger
