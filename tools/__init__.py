"""
Legion Tools Package

Collection of automation tools for Legion repository maintenance.
Includes auto-fix, conflict resolution, and sequential PR merge capabilities.
"""

__version__ = "1.0.0"

# Make tools available for import
from . import auto_fix
from . import auto_resolve_conflicts
from . import post_update
from . import sequential_pr_merge
from . import assurance_scan

__all__ = [
    "auto_fix",
    "auto_resolve_conflicts", 
    "post_update",
    "sequential_pr_merge",
    "assurance_scan"
] 