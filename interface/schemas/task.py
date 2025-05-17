"""
Pydantic schemas for Task related API operations.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Option 1: Define one set of names, conditionally.
# This relies on mypy correctly understanding that only one branch is taken.

# Attempt to import from core.db.models first. If this path is taken by mypy,
# it should not complain about the except block definitions if they are guarded.
# However, mypy might still analyze the except block independently.

_TaskStatus_imported = None
_TaskPriority_imported = None

try:
    from core.db.models import TaskPriority as _TaskPriority_imported_real
    from core.db.models import TaskStatus as _TaskStatus_imported_real

    _TaskStatus_imported = _TaskStatus_imported_real
    _TaskPriority_imported = _TaskPriority_imported_real
except ImportError:
    pass  # Fallback definitions will occur below if imports failed

if _TaskStatus_imported and _TaskPriority_imported:
    TaskStatus = _TaskStatus_imported
    TaskPriority = _TaskPriority_imported
else:
    from enum import Enum  # Keep import here for clarity if this branch is taken

    class TaskStatus(str, Enum):
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"

    class TaskPriority(int, Enum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3


# Base properties shared by all task schemas
class TaskBase(BaseModel):
    agent_id: Optional[str] = Field(
        None, description="Identifier of the agent assigned to the task."
    )
    type: Optional[str] = Field(None, description="Type or category of the task.")
    priority: TaskPriority = Field(
        TaskPriority.MEDIUM, description="Priority level of the task."
    )
    title: Optional[str] = Field(
        None, description="A short, descriptive title for the task."
    )
    description: Optional[str] = Field(
        None, description="Detailed description of the task's objective."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Arbitrary metadata associated with the task."
    )


# Properties to receive via API on task creation
class TaskCreate(TaskBase):
    agent_id: str = Field(
        ..., description="Identifier of the agent assigned to the task."
    )
    type: str = Field(..., description="Type or category of the task.")
    title: str = Field(..., description="A short, descriptive title for the task.")
    # Description and metadata can be optional on creation


# Properties to receive via API on task update (example, not strictly needed for phase 3 cancel)
class TaskUpdate(BaseModel):
    priority: Optional[TaskPriority] = None
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Properties shared by models stored in DB/returned by orchestrator
class TaskInDBBase(TaskBase):
    id: uuid.UUID = Field(..., description="Unique identifier for the task.")
    status: TaskStatus = Field(
        TaskStatus.PENDING, description="Current status of the task."
    )
    result: Optional[Any] = Field(
        None, description="Result of the task upon completion."
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the task was created."
    )
    started_at: Optional[datetime] = Field(
        None, description="Timestamp when the task processing started."
    )
    completed_at: Optional[datetime] = Field(
        None, description="Timestamp when the task processing completed."
    )
    error: Optional[str] = Field(None, description="Error message if the task failed.")

    class Config:
        orm_mode = True  # Compatible with ORM models
        # Pydantic v2 config:
        # from_attributes = True


# Properties to return to client
class Task(TaskInDBBase):
    pass  # Inherits all fields from TaskInDBBase


# Wrapper for returning a list of tasks
class TaskList(BaseModel):
    tasks: List[Task]
    total: int


# Schema for the response when a task is created
class TaskCreatedResponse(BaseModel):
    message: str = "Task submitted successfully."
    task_id: uuid.UUID
