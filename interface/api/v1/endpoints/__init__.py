"""
API v1 endpoints package - imports all router modules.
"""

from .agents import router as agents_router
from .auth import router as auth_router
from .lmstudio_proxy import router as lmstudio_proxy_router
from .login import router as login_router
from .memory import router as memory_router
from .system import router as system_router
from .tasks import router as tasks_router
from .tasks_registry import router as task_registry_router
from .echo import router as echo_router
from .queue import router as queue_router
from .metrics import router as metrics_router
from .agent import router as agent_router
from .middleware import router as middleware_router
# NOTE: handshake.py uses Flask Blueprint - excluded from FastAPI imports

__all__ = [
    "agents_router",
    "auth_router",
    "lmstudio_proxy_router",
    "login_router",
    "memory_router",
    "system_router",
    "tasks_router",
    "task_registry_router",
    "echo_router",
    "queue_router",
    "metrics_router",
    "agent_router",
    "middleware_router",
]
