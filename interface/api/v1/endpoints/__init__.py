try:  # pragma: no cover - optional deps may be missing in tests
    from .agent import router as agent_router
    from .agents import router as agents_router
    from .auth import router as auth_router
    from .demo import router as demo_router
    from .echo import router as echo_router
    from .handshake import bp as handshake_bp
    from .lmstudio_proxy import router as lmstudio_proxy_router
    from .login import router as login_router
    from .memory import router as memory_router
    from .metrics import router as metrics_router
    from .prompts import router as prompts_router
    from .queue import router as queue_router
    from .system import router as system_router
    from .tasks import router as tasks_router
    from .tasks_registry import router as task_registry_router
except Exception:  # pragma: no cover - endpoints unavailable
    agents_router = auth_router = lmstudio_proxy_router = None
    login_router = memory_router = system_router = None
    tasks_router = task_registry_router = None
    echo_router = queue_router = metrics_router = None
    agent_router = handshake_bp = prompts_router = demo_router = None

__all__ = [
    "agent_router",
    "agents_router",
    "auth_router",
    "demo_router",
    "echo_router",
    "handshake_bp",
    "lmstudio_proxy_router",
    "login_router",
    "memory_router",
    "metrics_router",
    "prompts_router",
    "queue_router",
    "system_router",
    "task_registry_router",
    "tasks_router",
]
