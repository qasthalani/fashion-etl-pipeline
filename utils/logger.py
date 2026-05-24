"""
logger.py

Centralized logging configuration for the ETL pipeline.
Outputs logs to both the console and a log file (etl_pipeline.log).
"""

import logging
import os


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a configured logger instance.

    Logs are written to both the console (INFO level and above)
    and to 'etl_pipeline.log' file (DEBUG level and above).

    Args:
        name (str): The logger name, typically the module's __name__.

    Returns:
        logging.Logger: A configured Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(log_dir, "..", "etl_pipeline.log")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger