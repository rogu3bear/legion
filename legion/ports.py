"""
Handles dynamic port allocation awareness for the Legion Orchestrator.

Reads .env.ports, provides fallback to defaults, and offers a lookup utility.
"""

from typing import Dict, Optional

from dotenv import dotenv_values

# Default ports for common services if not specified in .env.ports
DEFAULT_PORTS: Dict[str, int] = {
    "web": 8000,  # Standard for FastAPI/Uvicorn if not overridden
    "orchestrator": 5555,  # Default ZMQ/IPC for orchestrator if not in .env.ports
    "redis": 6379,
    "postgres": 5432,
    "prometheus": 9090,
    "grafana": 3000,
    "dev_frontend": 8000,  # Matches the default in existing docker-compose
}

RUNTIME_PORTS: Dict[str, int] = {}


def load_runtime_ports(env_file_path: str = ".env.ports") -> Dict[str, int]:
    """
    Loads port configurations from the specified .env file.
    Merges with defaults, prioritizing .env file values.
    Populates settings.runtime_ports.
    """
    global RUNTIME_PORTS
    env_ports = dotenv_values(env_file_path)

    loaded_ports: Dict[str, int] = {}

    # Start with defaults
    for key, port in DEFAULT_PORTS.items():
        loaded_ports[key] = port

    # Override with values from .env.ports if they exist and are valid integers
    for key, value in env_ports.items():
        if value is not None and key.startswith("PORT_ALLOCATOR_"):
            service_name = key.replace("PORT_ALLOCATOR_", "").lower()
            try:
                loaded_ports[service_name] = int(value)
            except ValueError:
                # Log a warning or handle error for non-integer port value if necessary
                print(
                    f"[Warning] Invalid port value for {key}: {value}. Using default if available."
                )

    RUNTIME_PORTS = loaded_ports
    return RUNTIME_PORTS


def get_port(service_key: str) -> Optional[int]:
    """
    Retrieves the allocated port for a given service key.

    Args:
        service_key: The lower-case key for the service (e.g., "redis").

    Returns:
        The port number if found, otherwise None.
    """
    return RUNTIME_PORTS.get(service_key)


# Initialize RUNTIME_PORTS on module load
load_runtime_ports()
