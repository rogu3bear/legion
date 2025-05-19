# NOTE: The previous version of this file (HEAD) implemented a thread-safe task repository with optional SQLite persistence.
# The current version (main) uses a JSON-backed StateRepo for agent/task/queue management.
# If SQL persistence is needed in the future, consider integrating the HEAD logic as an optional backend.

"""Thread-safe task repository with optional SQLite persistence."""

from __future__ import annotations

import argparse
import json
import logging
import os
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from sqlalchemy import JSON, Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

from legion.core.constants import TaskState

LEGION_DATA_DIR = Path(os.getenv("LEGION_DATA_DIR", "memory"))
BACKEND = os.getenv("LEGION_STATE_BACKEND", "memory")
DB_PATH = LEGION_DATA_DIR / "state" / "legion.db"

Base = declarative_base()
SessionLocal = sessionmaker()


class TaskModel(Base):
    __tablename__ = "task_registry"
    id = Column(String, primary_key=True)
    tags = Column(JSON, nullable=False, default=list)
    owner = Column(String, nullable=False)
    agent = Column(String)
    status = Column(String, nullable=False)


@dataclass
class TaskRecord:
    task_id: str
    tags: List[str]
    owner: str
    agent: Optional[str] = None
    status: TaskState = TaskState.PENDING


@dataclass
class AgentRecord:
    """Information stored for each registered agent."""

    id: str
    role: str
    capabilities: List[str]
    token: str
    registered_at: str


class _StateRepo:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._tasks: Dict[str, TaskRecord] = {}
        self._agents: Dict[str, AgentRecord] = {}
        self._session = None
        self._redis = None
        if redis is not None:
            try:
                redis_port = int(os.getenv("REDIS_PORT", 7810))
                self._redis = redis.Redis(
                    host="localhost", port=redis_port, decode_responses=True
                )
            except Exception:  # pragma: no cover - optional redis failure
                self._redis = None
        if BACKEND == "sqlite":
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            engine = create_engine(f"sqlite:///{DB_PATH}")
            Base.metadata.create_all(engine)
            SessionLocal.configure(bind=engine)
            self._session = SessionLocal()

    def _persist(self, rec: TaskRecord) -> None:
        if self._session is None:
            return
        obj = self._session.get(TaskModel, rec.task_id) or TaskModel(id=rec.task_id)
        obj.tags = rec.tags
        obj.owner = rec.owner
        obj.agent = rec.agent
        obj.status = rec.status.value
        self._session.add(obj)
        self._session.commit()

    def add_task(self, task_id: str, tags: List[str], owner: str, agent: Optional[str] = None) -> None:
        with self._lock:
            rec = TaskRecord(task_id, tags, owner, agent)
            self._tasks[task_id] = rec
            self._persist(rec)

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        with self._lock:
            return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        *,
        status: Optional[TaskState] = None,
        tags: Optional[List[str]] = None,
        owner: Optional[str] = None,
    ) -> Optional[TaskRecord]:
        with self._lock:
            rec = self._tasks.get(task_id)
            if rec is None:
                return None
            if status is not None:
                rec.status = status
            if tags is not None:
                rec.tags = tags
            if owner is not None:
                rec.owner = owner
            self._persist(rec)
            return rec

    def list_tasks(
        self,
        *,
        status: Optional[TaskState] = None,
        owner: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Iterable[TaskRecord]:
        with self._lock:
            for rec in self._tasks.values():
                if status is not None and rec.status != status:
                    continue
                if owner is not None and rec.owner != owner:
                    continue
                if tag is not None and tag not in rec.tags:
                    continue
                yield rec

    def remove_task(self, task_id: str) -> bool:
        with self._lock:
            rec = self._tasks.pop(task_id, None)
            if rec is None:
                return False
            if self._session is not None:
                obj = self._session.get(TaskModel, task_id)
                if obj:
                    self._session.delete(obj)
                    self._session.commit()
            return True

    # ------------------------------------------------------------------
    # Agent registration & lookup
    # ------------------------------------------------------------------
    def register_agent(self, agent_id: str, role: str, capabilities: List[str]) -> str:
        """Persist agent metadata and return auth token."""
        with self._lock:
            token = uuid.uuid4().hex
            record = AgentRecord(
                id=agent_id,
                role=role,
                capabilities=capabilities,
                token=token,
                registered_at=datetime.utcnow().isoformat(),
            )
            self._agents[agent_id] = record
            if self._redis:
                try:
                    self._redis.set(f"agent:{agent_id}", json.dumps(record.__dict__))
                except Exception:  # pragma: no cover - redis errors
                    pass
            logging.getLogger(__name__).info(
                "agent registered",
                extra={"props": {
                    "agent_id": agent_id,
                    "role": role,
                    "capabilities": capabilities,
                }},
            )
            return token

    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        """Retrieve agent metadata."""
        with self._lock:
            if self._redis:
                try:
                    raw = self._redis.get(f"agent:{agent_id}")
                    if raw:
                        data = json.loads(raw)
                        return AgentRecord(**data)
                except Exception:  # pragma: no cover - redis errors
                    pass
            return self._agents.get(agent_id)

    def get_agent_tasks(self, agent_id: str) -> List[TaskRecord]:
        """Return tasks currently associated with an agent."""
        with self._lock:
            return [t for t in self._tasks.values() if t.agent == agent_id]


_repo = _StateRepo()

add_task = _repo.add_task
get_task = _repo.get_task
update_task = _repo.update_task
list_tasks = _repo.list_tasks
remove_task = _repo.remove_task
register_agent = _repo.register_agent
get_agent = _repo.get_agent
get_agent_tasks = _repo.get_agent_tasks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--migrate", action="store_true", help="ensure database exists")
    args = parser.parse_args()
    if args.migrate and BACKEND == "sqlite":
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{DB_PATH}")
        Base.metadata.create_all(engine)
        print(f"migrated {DB_PATH}")


if __name__ == "__main__":
    main()
