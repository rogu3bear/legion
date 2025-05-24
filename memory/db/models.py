"""SQLAlchemy models for memory-related tables."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import the shared Base and Agent model
from legion.core.db.models import Base, Agent


class EchoLog(Base):
    """Simple echo log table."""

    __tablename__ = "echo_logs"

    id: str = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    payload: dict = Column(JSON, nullable=False)


class Conversation(Base):
    """Conversation threads initiated via the web interface."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    thread_id = Column(String, unique=True, index=True, nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("Agent")


class Directive(Base):
    """Directive text associated with an agent."""

    __tablename__ = "directives"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("Agent")
