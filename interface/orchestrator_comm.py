"""Module for communicating with the Legion Orchestrator via ZeroMQ."""

import json
import logging
import typing
from typing import Any, Dict, Optional

import zmq

from interface.core.config import settings

logger = logging.getLogger(__name__)

# --- ZeroMQ Configuration ---
ORCHESTRATOR_ADDRESS = settings.ORCHESTRATOR_ADDRESS
REQUEST_TIMEOUT_MS = 5000  # 5 seconds timeout

# --- ZeroMQ Context (Singleton recommended) ---
# Create context once per process. Handles potential errors during initialization.
try:
    context = zmq.Context.instance()  # Get singleton instance
    logger.info("ZeroMQ context initialized.")
except Exception as e:
    logger.critical(f"Failed to initialize ZeroMQ context: {e}", exc_info=True)
    # Set context to None to indicate failure; functions using it should check.
    context = None


def send_request(
    command: Dict[str, Any], timeout_ms: int = REQUEST_TIMEOUT_MS
) -> Optional[Dict[str, Any]]:
    """Sends a command to the orchestrator via ZeroMQ and awaits the response.

    Uses a REQ/REP pattern. Creates a new socket per request for thread-safety.
    Handles timeouts and communication errors.

    Args:
        command: Dictionary representing the command payload.
        timeout_ms: Maximum time to wait for a response in milliseconds.

    Returns:
        The response dictionary received from the orchestrator
        or None if timed out or an error occurred.
    """
    if context is None:
        logger.error("ZeroMQ context is not initialized. Cannot send command.")
        return None

    # Use a unique request ID for better log tracing, if available in command
    request_id = command.get("request_id", "N/A")
    socket = None  # Ensure socket is defined for the finally block

    try:
        # Create and connect a new socket for this request
        socket = context.socket(zmq.REQ)
        # Set LINGER to 0 to prevent blocking on close if messages are pending
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(ORCHESTRATOR_ADDRESS)
        logger.debug(
            f"ZMQ REQ socket connected to {ORCHESTRATOR_ADDRESS} for request ID {request_id}"
        )

        # Send the command as JSON
        logger.debug(f"Sending ZMQ request (ID: {request_id}): {json.dumps(command)}")
        socket.send_json(command)

        # Wait for the reply using poll with timeout
        if socket.poll(timeout_ms, zmq.POLLIN):
            response_raw = socket.recv_json()
            # Cast the response to the expected type
            response = typing.cast(Dict[str, Any], response_raw)
            logger.debug(
                f"Received ZMQ response (for ID: {request_id}): {json.dumps(response)}"
            )
            return response
        else:
            # Timeout occurred
            logger.warning(
                f"Timeout waiting for ZMQ response for request (ID: {request_id}) after {timeout_ms}ms"
            )
            return None

    except zmq.ZMQError as e:
        # Handle ZeroMQ specific errors
        logger.error(
            f"ZeroMQ communication error (Request ID: {request_id}): {e}", exc_info=True
        )
        return None
    except Exception as e:
        # Handle other potential errors (e.g., JSON decoding errors)
        logger.error(
            f"Unexpected error during ZMQ communication (Request ID: {request_id}): {e}",
            exc_info=True,
        )
        return None
    finally:
        # Ensure the socket is always closed
        if socket:
            try:
                socket.close()
                logger.debug(f"ZMQ REQ socket closed for request ID {request_id}")
            except Exception as e_close:
                # Log error during close but don't mask original error
                logger.error(
                    f"Error closing ZMQ socket for request ID {request_id}: {e_close}"
                    exc_info=True
                )


# Note: The previous file-based functions (send_command, await_response) and
# associated directory constants have been removed. Code importing them will fail.

# --- Example Usage (for testing/illustration) ---
# async def get_orchestrator_status():
#     command = {"action": "status"}
#     cmd_id = send_command(command)
#     response = await_response(cmd_id)
#     return response

# Alias for backward compatibility
send_orchestrator_request = send_request
