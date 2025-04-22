"""Logging configuration for Legion, providing structured JSON logging."""

import logging
import json
import sys

from typing import Dict, Any


def setup_logging(log_level: str = 'INFO') -> None:
    """
    Configure structured JSON logging for the Legion system.
    
    Args:
        log_level (str): The logging level to set (default: 'INFO').
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create a JSON formatter
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_data: Dict[str, Any] = {
                'timestamp': self.formatTime(record, self.datefmt),
                'level': record.levelname,
                'name': record.name,
                'message': record.getMessage(),
                'filename': record.filename,
                'funcName': record.funcName,
                'lineno': record.lineno,
            }
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            return json.dumps(log_data)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)
    
    logging.info('Logging initialized with JSON format', extra={'log_level': log_level}) 