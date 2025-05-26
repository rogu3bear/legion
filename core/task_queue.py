from __future__ import annotations

import json
from typing import Any


class TaskQueue:
    """Redis-backed task queue supporting priorities."""

    def __init__(self, redis_conn: Any) -> None:
        self.r = redis_conn
        self.priorities = ["high", "normal", "low"]

    def _key(self, agent_id: str, priority: str) -> str:
        return f"legion:queue:{agent_id}:{priority}"

    def enqueue_task(
        self, agent_id: str, task_dict: dict[str, Any], priority: str = "normal"
    ) -> None:
        data = json.dumps(task_dict)
        if priority == "high":
            self.r.lpush(self._key(agent_id, "high"), data)
        elif priority == "low":
            self.r.rpush(self._key(agent_id, "low"), data)
        else:
            self.r.rpush(self._key(agent_id, "normal"), data)

    def dequeue_task(self, agent_id: str) -> dict[str, Any] | None:
        for level in self.priorities:
            key = self._key(agent_id, level)
            raw = self.r.lpop(key)
            if raw is not None:
                if isinstance(raw, bytes):
                    raw = raw.decode()
                return json.loads(raw)
        return None

    def get_queue_length(self, agent_id: str) -> int:
        length = 0
        for level in self.priorities:
            length += self.r.llen(self._key(agent_id, level))
        return length
