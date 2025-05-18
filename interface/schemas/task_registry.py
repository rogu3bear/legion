from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    """Simplified task states for the registry API."""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    DONE = "DONE"
    FAILED = "FAILED"


class Task(BaseModel):
    """Public representation of a task in the in-memory registry."""

    id: str
    tags: List[str] = []
    owner: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    """Fields allowed for task updates."""

    status: Optional[TaskStatus] = None
    tags: Optional[List[str]] = None
    owner: Optional[str] = None
