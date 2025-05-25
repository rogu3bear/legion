"""Migration to create the tasks table.

This migration creates the tasks table for tracking agent task execution.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy import (
    Enum as SQLEnum,
)

from core.db.models import TaskPriority, TaskStatus

metadata = MetaData()


def upgrade(migrator: Any) -> None:
    """Create tasks table.

    Args:
        migrator: Migration context
    """
    Table(
        "tasks",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("agent_id", Integer, ForeignKey("agents.id"), nullable=False),
        Column("type", String, nullable=False),
        Column("status", SQLEnum(TaskStatus), default=TaskStatus.PENDING),
        Column("priority", SQLEnum(TaskPriority), default=TaskPriority.MEDIUM),
        Column("title", String(200), nullable=False),
        Column("description", String(2000)),
        Column("task_metadata", JSON, default=dict),
        Column("result", JSON),
        Column("created_at", DateTime, default=datetime.utcnow),
        Column("started_at", DateTime),
        Column("completed_at", DateTime),
        Column("error", String(1000)),
    ).create(migrator.bind)


def downgrade(migrator: Any) -> None:
    """Drop tasks table.

    Args:
        migrator: Migration context
    """
    Table("tasks", metadata).drop(migrator.bind)
