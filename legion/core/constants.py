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


# Agent name literals used throughout the codebase
ORCHESTRATOR_AGENT = "orchestrator"
ECHO_AGENT = "echo"
THERAPIST_AGENT = "therapist"
MIDDLEWARE_AGENT = "middleware"
METRICS_AGENT = "metrics"
PING_AGENT = "ping"
RESEARCHER_AGENT = "researcher"
INTERFACE_API_AGENT = "interface_api"

# Default conversational roles
DEFAULT_ROLES = {"user": "human", "agent": "ai"}


# Default port mapping reused across the project
DEFAULT_PORT_MAP: Dict[str, int] = DEFAULT_PORTS
