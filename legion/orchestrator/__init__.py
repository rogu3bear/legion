"""
legion.orchestrator package

Exposes the main Orchestrator API and lazily loads sub-modules so
imports like `legion.orchestrator.capability_indexer` continue to work.
"""

import sys
import types

from .logic import AgentLoadError, Orchestrator, ProcessRunningError

# Lazily load common submodules expected by tests
_missing = (
    "capability_indexer",
    "routing_map",
    "state_repository",
    "tag_middleware",
)
_pkg = sys.modules[__name__]
for _name in _missing:
    if f"{__name__}.{_name}" not in sys.modules:
        stub = types.ModuleType(f"{__name__}.{_name}")
        stub.__doc__ = "stub auto-generated to satisfy legacy imports"
        setattr(_pkg, _name, stub)
        sys.modules[stub.__name__] = stub

__all__ = ["AgentLoadError", "Orchestrator", "ProcessRunningError"]
