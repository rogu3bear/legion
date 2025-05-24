# mypy: ignore-errors
"""SQLAlchemy ORM models for Legion."""

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AgentStatus(enum.Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class Agent(Base):
    """Model for Legion agents and their runtime state."""

    __tablename__ = "agents"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False, unique=True)
    type: str = Column(String, nullable=False)
    status: AgentStatus = Column(
        Enum(AgentStatus), nullable=False, default=AgentStatus.OFFLINE
    )
    capabilities: List[Any] = Column(JSON, default=lambda: [])
    config: Dict[str, Any] = Column(JSON, default=lambda: {})
    agent_metadata: Dict[str, Any] = Column(JSON, default=lambda: {})
    is_active: bool = Column(Boolean, default=True)
    last_heartbeat: Optional[datetime] = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    tasks = relationship(
        "Task", back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agent {self.name}: {self.type} ({self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "config": self.config,
            "metadata": self.agent_metadata,
            "is_active": self.is_active,
            "last_heartbeat": self.last_heartbeat.isoformat()
            if self.last_heartbeat
            else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update_status(self, status: AgentStatus) -> None:
        """Update agent status and last heartbeat."""
        self.status = status
        self.last_heartbeat = datetime.utcnow()

    def get_pending_tasks(self) -> List["Task"]:
        """Get all pending tasks for this agent."""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    def get_active_task(self) -> Optional["Task"]:
        """Get the currently active task for this agent, if any."""
        active_tasks = [
            task for task in self.tasks if task.status == TaskStatus.IN_PROGRESS
        ]
        return active_tasks[0] if active_tasks else None


class Task(Base):
    """Model for tracking agent task execution and status."""

    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True)
    agent_id: int = Column(Integer, ForeignKey("agents.id"), nullable=False)
    type: str = Column(String, nullable=False)
    status: TaskStatus = Column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING
    )
    priority: TaskPriority = Column(
        Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM
    )
    title: str = Column(String, nullable=False)
    description: Optional[str] = Column(String, nullable=True)
    task_metadata: Dict[str, Any] = Column(JSON, default=lambda: {})
    result: Optional[Dict[str, Any]] = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Optional[datetime] = Column(DateTime, nullable=True)
    completed_at: Optional[datetime] = Column(DateTime, nullable=True)
    error: Optional[str] = Column(String, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.type} ({self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "type": self.type,
            "status": self.status.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "metadata": self.task_metadata,
            "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "error": self.error,
        }

    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark task as completed with optional result."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if result:
            self.result = result

    def fail(self, error: str) -> None:
        """Mark task as failed with error message."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error

    def cancel(self) -> None:
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
