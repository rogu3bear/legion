"""Core database models with typed SQLAlchemy."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean
    Column
    DateTime
    Enum
    ForeignKey
    Integer
    JSON
    String
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for typed SQLAlchemy models."""
    pass


class TaskStatus(enum.Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AgentStatus(enum.Enum):
    """Agent operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class Agent(Base):
    """Agent model with typed fields."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus), nullable=False, default=AgentStatus.OFFLINE
    )
    capabilities: Mapped[List[Any]] = mapped_column(JSON, default=list)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    agent_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agent {self.id}: {self.name} ({self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "id": self.id
            "name": self.name
            "type": self.type
            "status": self.status.value if self.status else None
            "capabilities": self.capabilities
            "config": self.config
            "agent_metadata": self.agent_metadata
            "is_active": self.is_active
            "last_heartbeat": (
                self.last_heartbeat.isoformat() if self.last_heartbeat else None
            )
            "created_at": self.created_at.isoformat() if self.created_at else None
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create agent from dictionary data."""
        # Parse datetime fields
        for field in ["last_heartbeat", "created_at", "updated_at"]:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])

        # Parse enum field
        if data.get("status"):
            data["status"] = AgentStatus(data["status"])

        return cls(**data)


class Task(Base):
    """Task model with typed fields."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    task_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.type} ({self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id
            "agent_id": self.agent_id
            "type": self.type
            "status": self.status.value if self.status else None
            "priority": self.priority.value if self.priority else None
            "title": self.title
            "description": self.description
            "task_metadata": self.task_metadata
            "result": self.result
            "created_at": self.created_at.isoformat() if self.created_at else None
            "started_at": self.started_at.isoformat() if self.started_at else None
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
            "error": self.error
        }
