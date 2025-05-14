import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON.
    """

    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "props") and isinstance(record.props, dict):
            log_record.update(record.props)  # For custom properties

        # Add extra fields from the log record, but exclude default ones we've handled
        # to avoid duplication
        for key, value in record.__dict__.items():
            if key not in ('args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                          'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
                          'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                          'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName',
                          'props') and not key.startswith('_'):
                log_record[key] = value
                
        return json.dumps(log_record)


def setup_legion_logging(
    log_level_str: str = "INFO", log_to_console: bool = True, log_file_path: Optional[str] = None
):
    """
    Configures structured JSON logging for the Legion application.

    Args:
        log_level_str: String representation of log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Whether to log to console
        log_file_path: Path to log file. If None, will not log to file.
    """
    # Convert string log level to logging module constant
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Create formatter for structured JSON output
    formatter = JsonFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplication when reconfiguring
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set up handlers
    handlers = []

    # Add file handler if path is provided
    if log_file_path:
        try:
            # Ensure directory exists for log file
            log_dir = Path(log_file_path).parent
            if log_dir.name and not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file_path, mode="a")  # Append mode
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            handlers.append(file_handler)
            
        except Exception as e:
            # Fallback to console logging if file handler setup fails
            print(
                f"Error setting up file logger at {log_file_path}: {e}. Logging to console only.",
                file=sys.stderr,
            )
            if not log_to_console:  # If console wasn't primary, ensure it's added now
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(formatter)
                handlers.append(console_handler)

    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # Ensure at least one handler exists
    if not handlers:
        print(
            "Warning: No log handlers explicitly configured. Defaulting to console output.",
            file=sys.stderr,
        )

    for handler in handlers:
        root_logger.addHandler(handler)

    # Override excepthook to log uncaught exceptions
    def log_uncaught_exception(exc_type, exc_value, exc_traceback):
        root_logger.error("Uncaught exception", 
                         exc_info=(exc_type, exc_value, exc_traceback))
        # Call the original exception handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = log_uncaught_exception

    # Configure logging for some common libraries to be less verbose or use the new format
    # For example, reduce verbosity of noisy libraries:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Can be very noisy

    # If using specific libraries that log a lot, you might want to attach your formatter to their loggers too,
    # or ensure they propagate to the root logger correctly.
    # For example, to ensure 'openai' logs also use JsonFormatter if they propagate to root:
    # logging.getLogger("openai").propagate = True # Default is True

    logging.info(
        "Structured JSON logging configured.",
        extra={
            "props": {
                "log_level": log_level_str,
                "console": log_to_console,
                "file": log_file_path,
            }
        },
    )

    return root_logger


# Test function to demonstrate logging
def _test_logging(log_level='DEBUG'):
    """Test function to demonstrate logging at various levels."""
    logger = logging.getLogger("test.logger")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test exception logging
    try:
        # Example exception
        raise ValueError("This is a test exception")
    except ValueError:
        logger.exception("A ValueError occurred!")
        
    # Log messages using different loggers to test hierarchical behavior
    logging.getLogger("test.sub1").info("Subsystem 1 message")
    logging.getLogger("test.sub2").warning("Subsystem 2 warning")
    
    # Custom fields in extra
    logger.info("Message with custom fields", extra={"taskName": "Task-123", "user_id": 42, "component": "API"})
    
    # Example of how error handling would look in real code:
    # try:
    #    response = httpx.get("https://example.com/api")
    # except httpx.ConnectError as e:
    #      logging.getLogger("httpx.test").error(f"HTTPX connect error: {e}") # this will use root logger formatting
    
    print(f"Test logs generated. Check console output and '{log_file_env}' if configured.")


if __name__ == "__main__":
    # Example of using the logging utility
    log_file_env = os.environ.get("LEGION_LOG_FILE", "logs/legion.log")
    logger = setup_legion_logging(log_level_str="DEBUG", log_to_console=True, log_file_path=log_file_env)
    _test_logging()
