from __future__ import annotations

import json
from typing import Any, Dict, Optional


class TaskQueue:
    """Redis-backed task queue supporting priorities."""

    def __init__(self, redis_conn: Any) -> None:
        self.r = redis_conn
        self.priorities = ["high", "normal", "low"]

    def _key(self, agent_id: str, priority: str) -> str:
        return f"legion:queue:{agent_id}:{priority}"

    def enqueue_task(
        self, agent_id: str, task_dict: Dict[str, Any], priority: str = "normal"
    ) -> None:
        data = json.dumps(task_dict)
        if priority == "high":
            self.r.lpush(self._key(agent_id, "high"), data)
        elif priority == "low":
            self.r.rpush(self._key(agent_id, "low"), data)
        else:
            self.r.rpush(self._key(agent_id, "normal"), data)

    def dequeue_task(self, agent_id: str) -> Optional[Dict[str, Any]]:
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

    def clear_queue(self, agent_id: str) -> None:
        """Clear all tasks for an agent across all priorities."""
        for level in self.priorities:
            self.r.delete(self._key(agent_id, level))

    def get_queue_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all agent queues."""
        stats = {}
        pattern = "legion:queue:*"
        for key in self.r.scan_iter(match=pattern):
            key_str = key.decode() if isinstance(key, bytes) else str(key)
            parts = key_str.split(":")
            if len(parts) >= 4:
                agent_id = parts[2]
                priority = parts[3]
                if agent_id not in stats:
                    stats[agent_id] = {"high": 0, "normal": 0, "low": 0}
                stats[agent_id][priority] = self.r.llen(key)
        return stats 