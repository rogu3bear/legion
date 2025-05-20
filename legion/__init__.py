"""Legion package init."""

try:  # pragma: no cover - optional during tests
    from .orchestrator import Orchestrator
except Exception:  # pragma: no cover
    Orchestrator = None

__all__ = ["Orchestrator"]
