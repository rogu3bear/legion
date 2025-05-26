"""Redis-backed task queue with basic state tracking."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None


@dataclass
class Task:
    id: str
    agent: str
    payload: dict
    priority: int = 0
    state: str = "queued"
    retries: int = 0
    max_retries: int = 3
    available_at: float = 0.0


class TaskQueue:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 7810,
        max_retries: int = 5,
        base_delay: int = 5,
    ) -> None:
        if redis is None:
            self.client = None
            self.store: dict[str, Task] = {}
            self.dead_letter: dict[str, Task] = {}
        else:
            self.client = redis.Redis(host=host, port=port, decode_responses=True)
            self.dead_letter_key = "dead_tasks"
        self.max_retries = max_retries
        self.base_delay = base_delay

    def enqueue(self, task: Task) -> None:
        logger = logging.getLogger(__name__)
        if not task.available_at:
            task.available_at = time.time()
        if self.client:
            self.client.set(f"task:{task.id}", json.dumps(task.__dict__))
            score = task.priority * 1_000_000 + int(task.available_at)
            self.client.zadd("task_queue", {task.id: score})
            self.client.set(f"task:{task.id}:retry_count", 0)
        else:
            self.store[task.id] = task
        logger.info(
            "task enqueued",
            extra={"props": {"task_id": task.id, "agent": task.agent, "priority": task.priority}},
        )

    def dequeue(self, agent: str) -> Task | None:
        if self.client:
            ids = self.client.zrange("task_queue", 0, -1)
            now = time.time()
            for task_id in ids:
                raw = self.client.get(f"task:{task_id}")
                if not raw:
                    self.client.zrem("task_queue", task_id)
                    continue
                data = json.loads(raw)
                if data.get("available_at", 0) > now:
                    continue
                if data.get("agent") == agent and data.get("state") == "queued":
                    data["state"] = "in_progress"
                    self.client.set(f"task:{task_id}", json.dumps(data))
                    self.client.zrem("task_queue", task_id)
                    return Task(**data)
            return None
        else:
            now = time.time()
            queued = [
                t
                for t in self.store.values()
                if t.agent == agent and t.state == "queued" and t.available_at <= now
            ]
            if not queued:
                return None
            queued.sort(key=lambda t: t.priority)
            task = queued[0]
            task.state = "in_progress"
            return task

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        if self.client:
            keys = self.client.keys("task:*")
            items = [json.loads(self.client.get(k)) for k in keys]
        else:
            items = [t.__dict__ for t in self.store.values()]
        for data in items:
            state = data.get("state", "queued")
            counts[state] = counts.get(state, 0) + 1
        return counts

    def retry_task(self, task_id: str) -> None:
        logger = logging.getLogger(__name__)
        task = self.get(task_id)
        if not task:
            return
        task.retries += 1
        if task.retries > self.max_retries:
            task.state = "failed"
            if self.client:
                self.client.set(f"task:{task_id}", json.dumps(task.__dict__))
                self.client.rpush(self.dead_letter_key, task_id)
            else:
                self.dead_letter[task_id] = task
            logger.error(
                "task failed",
                extra={"props": {"task_id": task_id, "retries": task.retries}},
            )
            return
        delay = min(self.base_delay * 2 ** (task.retries - 1), 60)
        task.state = "queued"
        task.priority += 1
        task.available_at = time.time() + delay
        if self.client:
            self.client.set(f"task:{task_id}", json.dumps(task.__dict__))
            score = task.priority * 1_000_000 + int(task.available_at)
            self.client.zadd("task_queue", {task_id: score})
            self.client.set(f"task:{task_id}:retry_count", task.retries)
        else:
            self.store[task_id] = task
        logger.info(
            "task retry",
            extra={"props": {"task_id": task_id, "attempt": task.retries, "delay": delay}},
        )

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

    def get(self, task_id: str) -> Task | None:
        if self.client:
            raw = self.client.get(f"task:{task_id}")
            if raw:
                data = json.loads(raw)
                return Task(**data)
            return None
        return self.store.get(task_id)

    def record_failure(self, task_id: str, error: str) -> None:
        """Handle task failure with retry and logging."""
        logger = logging.getLogger(__name__)
        if self.client:
            self.client.rpush(f"task:{task_id}:error_log", json.dumps({"error": error, "ts": time.time()}))
        if self.get(task_id):
            self.retry_task(task_id)
            logger.error("task error", extra={"props": {"task_id": task_id, "error": error}})
        else:
            logger.error("unknown task", extra={"props": {"task_id": task_id}})


queue = TaskQueue()
