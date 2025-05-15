"""Task model for tracking agent tasks and their execution status.

This module defines the Task model which represents work items assigned to Legion agents.
Each task has a type, status, associated agent, and execution metadata.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Session, relationship

from .base import BaseModel


class TaskStatus(str, Enum):
    """Enumeration of possible task statuses."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Enumeration of supported task types."""

    RESEARCH = "research"
    CODE = "code"
    ANALYSIS = "analysis"
    CHAT = "chat"
    SYSTEM = "system"


class Task(BaseModel):
    """Model for tracking agent tasks and their execution.

    Attributes:
        id: Unique identifier for the task
        agent_id: ID of the agent assigned to this task
        type: Type of task (research, code, etc.)
        status: Current execution status
        priority: Task priority (1-5, higher is more important)
        title: Brief description of the task
        description: Detailed task description/requirements
        metadata: Additional task-specific metadata as JSON
        result: Task execution result/output as JSON
        created_at: When the task was created
        started_at: When task execution began
        completed_at: When task execution finished
        error: Error message if task failed
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    type = Column(SQLEnum(TaskType), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Integer, default=3)
    title = Column(String(200), nullable=False)
    description = Column(String(2000))
    metadata = Column(JSON, default=dict)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error = Column(String(1000))

    # Relationship to the agent
    agent = relationship("Agent", backref="tasks")

    def __repr__(self) -> str:
        """String representation of Task instance."""
        return f"<Task(id={self.id}, type='{self.type}', status='{self.status}')>"

    @classmethod
    def get_pending(
        cls, session: Session, agent_id: Optional[int] = None
    ) -> List["Task"]:
        """Get pending tasks, optionally filtered by agent.

        Args:
            session: Database session
            agent_id: Optional agent ID to filter by

        Returns:
            List[Task]: List of pending task instances
        """
        query = session.query(cls).filter(cls.status == TaskStatus.PENDING)
        if agent_id:
            query = query.filter(cls.agent_id == agent_id)
        return query.order_by(cls.priority.desc(), cls.created_at.asc()).all()

    def start(self, session: Session) -> None:
        """Mark task as started.

        Args:
            session: Database session
        """
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        session.add(self)
        session.commit()

    def complete(self, session: Session, result: Dict[str, Any]) -> None:
        """Mark task as completed with results.

        Args:
            session: Database session
            result: Task execution results
        """
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()
        session.add(self)
        session.commit()

    def fail(self, session: Session, error: str) -> None:
        """Mark task as failed with error message.

        Args:
            session: Database session
            error: Error message describing the failure
        """
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()
        session.add(self)
        session.commit()

    def cancel(self, session: Session) -> None:
        """Mark task as cancelled.

        Args:
            session: Database session
        """
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        session.add(self)
        session.commit()
