from pydantic import BaseModel

from interface.schemas.agent import (
    AgentActionResponse
    AgentConfigUpdate
    AgentCreate
    AgentStatusInfo
    AgentUpdate
)
from interface.schemas.task import Task, TaskCreate, TaskCreatedResponse, TaskList

# Re-export schemas for easier importing in API endpoints
__all__ = [
    "AgentActionResponse",
    "AgentConfigUpdate",
    "AgentCreate",
    "AgentStatusInfo",
    "AgentUpdate",
    "Task",
    "TaskCreate",
    "TaskCreatedResponse",
    "TaskList",
]


class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    status: str

    class Config:
        orm_mode = True


class AgentBase(BaseModel):
    name: str
    role: str


class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: int
    status: str

    class Config:
        orm_mode = True
