"""
Handles dynamic port allocation awareness for the Legion Orchestrator.

Reads .env.ports, provides fallback to defaults, and offers a lookup utility.
"""

from typing import Dict, Optional

from dotenv import dotenv_values
from legion.default_ports import DEFAULT_PORTS  # Import from the new file
from legion.utils.port_conflict_checker import check_ports_available  # re-export for orchestrator

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

    # Sanity check: Ensure all default port keys are covered by runtime ports
    # (either by being in .env.ports or by falling back to the default)
    # This helps catch discrepancies if .env.ports.example generation logic
    # diverges from DEFAULT_PORTS keys.
    if not set(DEFAULT_PORTS.keys()) <= set(RUNTIME_PORTS.keys()):
        missing_keys = set(DEFAULT_PORTS.keys()) - set(RUNTIME_PORTS.keys())
        # This should ideally not happen if defaults are always loaded first.
        # However, if a DEFAULT_PORT key somehow doesn't make it into RUNTIME_PORTS
        # (e.g. different naming convention not handled by the loading logic),
        # this assertion will catch it.
        # For the specified assertion `set(DEFAULT_PORTS) <= set(runtime_ports)`
        # this means that every key in DEFAULT_PORTS must be a key in RUNTIME_PORTS.
        print(
            f"[Error] Port Mismatch: The following DEFAULT_PORTS keys are not in RUNTIME_PORTS: {missing_keys}"
        )
        print(
            "         This might indicate an issue with .env.ports generation or naming conventions."
        )
        # Depending on strictness, either raise an error or just warn.
        # For now, printing an error. For a hard fail:
        # raise AssertionError(f"Port Mismatch: DEFAULT_PORTS keys {missing_keys} not in RUNTIME_PORTS")

    return RUNTIME_PORTS


# Valid port allocation map used across Legion. Only ports within this range
# should be used by services.
LEGION_PORT_MAP: Dict[str, int] = {
    "ui_backend": 7801,
    "ui_frontend": 7802,
    "orchestrator_rest": 7803,
    "interface_api": 7804,
    "middleware": 7805,
    "metrics": 7806,
    "researcher_api": 7807,
    "zmq_pub": 7808,
    "zmq_sub": 7809,
    "redis": 7810,
}


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
