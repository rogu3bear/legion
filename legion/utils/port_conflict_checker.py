import logging  # Import logging
import socket
from typing import Dict
from legion.default_ports import DEFAULT_PORTS

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Or your desired log level

# Port ranges for different environments
PORT_RANGES = {
    "development": (27000, 28000)
    "production": (31000, 32000)
    "testing": (29000, 30000)
}


def validate_port_range(port: int, environment: str = "development") -> bool:
    """
    Validates that a port falls within the allowed range for the environment.

    Args:
        port: The port number to validate
        environment: The environment to check against (development/production/testing)

    Returns:
        bool: True if port is in range, False otherwise
    """
    if environment not in PORT_RANGES:
        raise ValueError(f"Unknown environment: {environment}")

    min_port, max_port = PORT_RANGES[environment]
    return min_port <= port <= max_port


def check_ports_available(
    port_map: Dict[str, int], environment: str = "development"
) -> None:
    """
    Checks if ports are available and within the allowed range.

    Args:
        port_map: Dictionary mapping service names to port numbers
        environment: The environment to validate against

    Raises:
        RuntimeError: If any port is in use or out of range
    """
    conflicts = []
    range_violations = []

    # First check port ranges
    for service, port in port_map.items():
        # Skip LMStudio port and default ports loaded from DEFAULT_PORTS
        if port == 1234 or service in DEFAULT_PORTS:
            logger.debug(f"Skipping range check for port {port} (service: {service})")
            continue
        if not validate_port_range(port, environment):
            range_violations.append((service, port))

    if range_violations:
        violation_list = ", ".join(f"{svc}@{prt}" for svc, prt in range_violations)
        raise RuntimeError(f"Port range violations detected: {violation_list}")

    # Then check port availability
    for service, port in port_map.items():
        # Skip LMStudio port and default ports loaded from DEFAULT_PORTS
        if port == 1234 or service in DEFAULT_PORTS:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("0.0.0.0", port))
            except OSError:
                conflicts.append((service, port))

    if conflicts:
        conflict_list = ", ".join(f"{svc}@{prt}" for svc, prt in conflicts)
        raise RuntimeError(f"Port conflicts detected: {conflict_list}")
