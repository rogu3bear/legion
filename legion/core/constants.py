from enum import Enum
from typing import Dict

from legion.default_ports import DEFAULT_PORTS

# Environment variable keys
ORCHESTRATOR_ADDRESS_ENV = "ORCHESTRATOR_ADDRESS"
PORT_ENV_PREFIX = "PORT_ALLOCATOR_"


class TaskState(str, Enum):
    """Lifecycle states for tasks."""

    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"
    FAILED = "failed"


class AgentRole(str, Enum):
    """Known agent roles."""

    ARCHITECT = "architect"
    METRICS = "metrics"
    UX_DESIGNER = "ux_designer"
    THERAPIST = "therapist"
    PING = "ping"
    ECHO = "echo"
    HEALTHCHECK = "healthcheck"


# Default port mapping reused across the project
DEFAULT_PORT_MAP: Dict[str, int] = DEFAULT_PORTS
