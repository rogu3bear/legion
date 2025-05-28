"""In-memory task registry used by the orchestrator."""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from legion.core.constants import TaskState


@dataclass
class TaskRecord:
    """Represents a single tracked task."""

    task_id: str
    tags: List[str]
    owner: str
    agent: Optional[str] = None
    status: TaskState = TaskState.PENDING


def _default_registry() -> Dict[str, TaskRecord]:
    return {}


_TASK_REGISTRY: Dict[str, TaskRecord] = _default_registry()


def add_task(task_id: str, tags: List[str], owner: str, agent: Optional[str] = None) -> None:
    """Register a new task with default status PENDING."""

    _TASK_REGISTRY[task_id] = TaskRecord(
        task_id=task_id, tags=tags, owner=owner, agent=agent
    )


def update_task_status(task_id: str, status: TaskState) -> bool:
    """Update the status of a tracked task."""

    record = _TASK_REGISTRY.get(task_id)
    if record is None:
        return False
    record.status = status
    return True


def update_task(
    task_id: str
    *
    status: Optional[TaskState] = None
    tags: Optional[List[str]] = None
    owner: Optional[str] = None
) -> Optional[TaskRecord]:
    """Update fields on an existing task record."""

    record = _TASK_REGISTRY.get(task_id)
    if record is None:
        return None
    if status is not None:
        record.status = status
    if tags is not None:
        record.tags = tags
    if owner is not None:
        record.owner = owner
    return record


def get_task(task_id: str) -> Optional[TaskRecord]:
    """Retrieve a task record by ID."""

    return _TASK_REGISTRY.get(task_id)


def list_tasks(
    *
    status: Optional[TaskState] = None
    owner: Optional[str] = None
    tag: Optional[str] = None
) -> Iterable[TaskRecord]:
    """List tasks matching optional filters."""

    for record in _TASK_REGISTRY.values():
        if status is not None and record.status != status:
            continue
        if owner is not None and record.owner != owner:
            continue
        if tag is not None and tag not in record.tags:
            continue
        yield record


def remove_task(task_id: str) -> bool:
    """Delete a task from the registry."""

    return _TASK_REGISTRY.pop(task_id, None) is not None
