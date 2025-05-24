# import yaml  # Removed: stub package purged. Use a minimal local YAML loader if needed.
# import zmq.asyncio  # Removed: stub package purged. Use a minimal local zmq helper if needed, or wrap in try/except ImportError if optional.


# Import the new structured logging setup

# Define the classes directly to avoid circular imports
class ProcessRunningError(Exception):
    """Raised when a process is already running or there's a lock conflict."""
    pass


class AgentLoadError(Exception):
    """Raised when agent loading/importing fails."""
    pass


# Import Orchestrator after defining error classes
from ..orchestrator import Orchestrator

__all__ = ["AgentLoadError", "Orchestrator", "ProcessRunningError"]
