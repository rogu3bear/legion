"""SQLAlchemy models for memory-related tables."""
from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from interface.db.base import Base


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
