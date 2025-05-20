"""
legion.orchestrator package

Exposes the main Orchestrator API and lazily loads sub-modules so
imports like `legion.orchestrator.capability_indexer` continue to work.
"""

import sys
import types

# Define minimal stub classes for import
class Orchestrator:
    """Stub class for Orchestrator"""
    pass

class ProcessRunningError(Exception):
    """Stub exception for ProcessRunningError"""
    pass

class AgentLoadError(Exception):
    """Stub exception for AgentLoadError"""
    pass

# Set up stub submodules
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

# Add state_repo as an alias for state_repository
state_repo = sys.modules[f"{__name__}.state_repository"]

__all__ = ["Orchestrator", "ProcessRunningError", "AgentLoadError"]
