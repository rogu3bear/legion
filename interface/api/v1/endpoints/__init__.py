"""FastAPI v1 endpoints package."""

from importlib import import_module

__all__ = []

_modules = [
    "agents",
    "auth",
    "lmstudio_proxy",
    "login",
    "memory",
    "system",
    "tasks",
    "tasks_registry",
    "echo",
    "queue",
    "metrics",
    "agent",
    "middleware",
]

for _name in _modules:
    try:
        mod = import_module(f".{_name}", __name__)
        globals()[f"{_name}_router"] = getattr(mod, "router")
        __all__.append(f"{_name}_router")
    except Exception:  # pragma: no cover - allow partial availability
        continue
