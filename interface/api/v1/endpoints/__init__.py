try:  # pragma: no cover - optional deps may be missing in tests
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
    from .handshake import bp as handshake_bp
except Exception as e:  # pragma: no cover - endpoints unavailable
    print(f"ROUTER IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    agents_router = auth_router = lmstudio_proxy_router = None
    login_router = memory_router = system_router = None
    tasks_router = task_registry_router = None
    echo_router = queue_router = metrics_router = None
    agent_router = handshake_bp = None

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
    "handshake_bp",
]
