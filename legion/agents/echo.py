from __future__ import annotations

import json
import os
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None

from memory.db.models import Base, EchoLog


class EventSchema(BaseModel):
    """Simple event payload for EchoAgent logging."""

    payload: dict


class EchoEvent(BaseModel):
    """Structured event for the Echo logger."""

    timestamp: float
    level: str
    agent_id: str
    payload: dict


class EchoAgent:
    """Logging helper that persists events to the database."""

    def __init__(
        self, db_url: Optional[str] = None, redis_url: Optional[str] = None
    ) -> None:
        db_url = db_url or os.getenv(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///memory/db/legion.db"
        )
        connect_args = (
            {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        )
        self._engine = create_engine(db_url, connect_args=connect_args)
        Base.metadata.create_all(self._engine)
        self._SessionLocal = sessionmaker(bind=self._engine)
        self._redis = None
        if redis_url and redis is not None:
            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
            except Exception:
                self._redis = None

    def log(self, event: EventSchema) -> str:
        """Persist the event and return its UUID."""
        session: Session = self._SessionLocal()
        try:
            row = EchoLog(payload=event.payload)
            session.add(row)
            session.commit()
            uid = row.id
        finally:
            session.close()
        if self._redis is not None:
            try:
                self._redis.rpush("echo:log", json.dumps(event.payload))
            except Exception:
                pass
        return uid

    def record(self, event: EchoEvent) -> None:
        """Record an EchoEvent to Redis with secondary indexes."""
        if self._redis is None:
            return
        data = event.model_dump()
        encoded = json.dumps(data)
        try:
            self._redis.rpush("echo:events", encoded)
            self._redis.zadd(f"echo:by_level:{event.level}", {encoded: event.timestamp})
            self._redis.zadd(
                f"echo:by_agent:{event.agent_id}", {encoded: event.timestamp}
            )
            try:
                from legion.utils.agent_feed import post_agent_feed

                post_agent_feed(f"Echo recorded: {event.level}")
            except Exception:
                pass
        except Exception:
            pass
