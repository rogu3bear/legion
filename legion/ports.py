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
    "chroma": 27020,  # Default port for ChromaDB
    "test_metrics_server": 9100,  # Unified test metrics server port
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


def get_chroma_url(default_host: str = "localhost") -> str:
    """
    Constructs the Chroma API URL using the configured port.

    Args:
        default_host: The default host for Chroma, e.g., 'localhost'.

    Returns:
        The full Chroma API URL string.
    """
    port = get_port("chroma")
    # If chroma port is not found, it might indicate a configuration issue.
    # For now, we'll assume it should always be available either from defaults or .env.ports
    # A more robust solution might raise an error or have a fallback mechanism if port is None.
    if port is None:
        # This case should ideally not happen if 'chroma' is in DEFAULT_PORTS
        # and load_runtime_ports() runs correctly.
        # Fallback to a common default or raise an error.
        # For now, let's use the default port directly if get_port somehow fails to return it.
        port = DEFAULT_PORTS.get(
            "chroma", 8000
        )  # Defaulting to 8000 as a last resort example if not found
        print(
            f"[Warning] Chroma port not found in RUNTIME_PORTS, falling back to {port}. Check configuration."
        )
    return f"http://{default_host}:{port}"


# Initialize RUNTIME_PORTS on module load
load_runtime_ports()
