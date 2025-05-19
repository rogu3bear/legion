"""Redis-backed task queue with basic state tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None


@dataclass
class Task:
    id: str
    agent: str
    payload: dict
    state: str = "queued"


class TaskQueue:
    def __init__(self, host: str = "localhost", port: int = 7810) -> None:
        if redis is None:
            self.client = None
            self.store: Dict[str, Task] = {}
        else:
            self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def enqueue(self, task: Task) -> None:
        if self.client:
            self.client.set(f"task:{task.id}", json.dumps(task.__dict__))
        else:
            self.store[task.id] = task

    def dequeue(self, agent: str) -> Optional[Task]:
        if self.client:
            keys = self.client.keys("task:*")
            for key in keys:
                raw = self.client.get(key)
                if not raw:
                    continue
                data = json.loads(raw)
                if data.get("agent") == agent and data.get("state") == "queued":
                    data["state"] = "in_progress"
                    self.client.set(key, json.dumps(data))
                    return Task(**data)
            return None
        else:
            for _tid, task in list(self.store.items()):
                if task.agent == agent and task.state == "queued":
                    task.state = "in_progress"
                    return task
            return None

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        items = (
            [json.loads(self.client.get(k)) for k in self.client.keys("task:*")] if self.client else [t.__dict__ for t in self.store.values()]
        )
        for data in items:
            state = data.get("state", "queued")
            counts[state] = counts.get(state, 0) + 1
        return counts

    def update_state(self, task_id: str, state: str) -> None:
        if self.client:
            raw = self.client.get(f"task:{task_id}")
            if raw:
                data = json.loads(raw)
                data["state"] = state
                self.client.set(f"task:{task_id}", json.dumps(data))
        else:
            if task_id in self.store:
                self.store[task_id].state = state

    def get(self, task_id: str) -> Optional[Task]:
        if self.client:
            raw = self.client.get(f"task:{task_id}")
            if raw:
                data = json.loads(raw)
                return Task(**data)
            return None
        return self.store.get(task_id)


queue = TaskQueue()

