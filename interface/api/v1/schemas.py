from typing import List

from pydantic import BaseModel, Field

from interface.schemas.agent import (
    AgentActionResponse,
    AgentConfigUpdate,
    AgentCreate,
    AgentStatusInfo,
    AgentUpdate,
)
from interface.schemas.task import Task, TaskCreate, TaskCreatedResponse, TaskList


class ChatMessage(BaseModel):
    """Chat message model for structured communication."""
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Structured chat request for LM Studio."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(256, ge=1, le=4096, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Return streaming SSE/NDJSON response")


# Re-export schemas for easier importing in API endpoints
__all__ = [
    "AgentActionResponse",
    "AgentConfigUpdate",
    "AgentCreate",
    "AgentStatusInfo",
    "AgentUpdate",
    "ChatMessage",
    "ChatRequest",
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
