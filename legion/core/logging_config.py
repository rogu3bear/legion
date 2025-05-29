"""Logging configuration for Legion, providing structured JSON logging."""

import json
import logging
import sys
from typing import Any, Dict


def setup_logging(name: str = None, log_level: str = "INFO") -> logging.Logger:
    """
    Configure structured JSON logging for the Legion system.

    Args:
        name (str): The name for the logger (optional).
        log_level (str): The logging level to set (default: 'INFO').
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create a JSON formatter
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_data: Dict[str, Any] = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
                "filename": record.filename,
                "funcName": record.funcName,
                "lineno": record.lineno
            }
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_data)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(console_handler)

    # Create and return named logger if specified
    logger = logging.getLogger(name) if name else root_logger
    logger.info("Logging initialized with JSON format", extra={"log_level": log_level})
    
    return logger
