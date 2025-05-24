"""Redis-backed priority queue interface.

The queue uses a Redis sorted set for ordering and a hash to store task data
by ID. Tasks with lower ``priority`` values are dequeued first.  Timestamps are
mixed into the sorted set score to provide FIFO ordering among equal
priorities.

Example usage::

    r = redis.StrictRedis(decode_responses=True)
    q = PriorityQueue(r)
    q.enqueue({"action": "echo"}, priority=1)
    task = q.dequeue()

``ack`` simply removes the stored task data while ``retry`` pushes it back on
the queue with an incremented retry counter.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    import redis
except Exception:  # pragma: no cover - fallback during offline tests
    redis = None


class PriorityQueue:
    """Simple Redis-backed priority queue."""

    KEY = "queue:tasks"
    TASK_HASH = "queue:taskdata"

    def __init__(self, r: Optional[Any] = None) -> None:
        if r is not None:
            self.r = r
        else:
            if redis is None:  # pragma: no cover - tests provide a stub
                raise RuntimeError("Redis library not available")
            self.r = redis.StrictRedis(decode_responses=True)

    def enqueue(self, task: Dict[str, Any], priority: int = 5) -> str:
        """Enqueue a task and return its id."""

        tid = task.setdefault("id", str(uuid.uuid4()))
        task["priority"] = priority
        score = priority * 1_000_000 + int(time.time())
        self.r.hset(self.TASK_HASH, tid, json.dumps(task))
        self.r.zadd(self.KEY, {tid: score})
        return tid

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Retrieve the highest priority task or ``None`` if empty."""

        pipe = self.r.pipeline()
        pipe.zrange(self.KEY, 0, 0)
        pipe.zremrangebyrank(self.KEY, 0, 0)
        ids, _ = pipe.execute()
        if not ids:
            return None
        tid = ids[0]
        raw = self.r.hget(self.TASK_HASH, tid)
        if raw is None:
            return None
        return json.loads(raw)

    def ack(self, task_id: str) -> None:
        """Acknowledge completion of a task."""

        self.r.hdel(self.TASK_HASH, task_id)

    def retry(self, task_id: str) -> None:
        """Requeue a task with incremented retry count."""

        raw = self.r.hget(self.TASK_HASH, task_id)
        if raw is None:
            return
        task = json.loads(raw)
        task["retries"] = task.get("retries", 0) + 1
        priority = task.get("priority", 5)
        score = priority * 1_000_000 + int(time.time())
        self.r.hset(self.TASK_HASH, task_id, json.dumps(task))
        self.r.zadd(self.KEY, {task_id: score})
