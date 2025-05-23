from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for memory DB models."""


class EchoLog(Base):
    """Simple echo log table."""

    __tablename__ = "echo_logs"

    id: str = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    payload: dict = Column(JSON, nullable=False)
