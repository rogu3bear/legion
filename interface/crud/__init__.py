"""CRUD module initialization.

Exposes CRUD objects for different models.
"""

# Imports are exposed for external modules/tests.  Keep them minimal to avoid
# heavy dependencies during import-time (especially DB connections).

# from .crud_item import item
# Import agent CRUD if it's intended for direct API management
# otherwise, agent actions are likely handled via orchestrator comms.
# from .crud_agent import agent  # Example if direct DB CRUD for agents exists

# Re-export explicit CRUD functions rather than aliasing the *module*; this
# prevents circular-import issues seen in tests expecting `interface.crud.crud_task`.
# TEMPORARILY DISABLED - crud_task has syntax errors blocking startup
# from .crud_task import (
#     cancel_task,
#     create_task,
#     get_task,
#     list_tasks
# )

__all__ = [
    # "cancel_task",
    # "create_task", 
    # "get_task",
    # "list_tasks"
]
