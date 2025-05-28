"""Redis-backed task queue with optimized priority scheduling."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional, List
import time
import os

import logging

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
        self
        host: str = "localhost"
        port: int = None
        max_retries: int = 5
        base_delay: int = 5
    ) -> None:
        if redis is None:
            self.client = None
            self.store: Dict[str, Task] = {}
            self.dead_letter: Dict[str, Task] = {}
            self.agent_queues: Dict[str, List[Task]] = {}
        else:
            self.client = redis.Redis(host=host, port=port, decode_responses=True)
            self.dead_letter_key = "dead_tasks"
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.port = port if port is not None else int(os.getenv("REDIS_PORT", 7600))

    def _agent_queue_key(self, agent: str) -> str:
        """Generate Redis key for agent-specific queue."""
        return f"agent_queue:{agent}"

    def enqueue(self, task: Task) -> None:
        logger = logging.getLogger(__name__)
        if not task.available_at:
            task.available_at = time.time()
        
        if self.client:
            # Store task data
            self.client.set(f"task:{task.id}", json.dumps(task.__dict__))
            
            # Add to agent-specific sorted set for efficient dequeue
            # Score: priority (lower = higher priority) + timestamp for FIFO within priority
            score = task.priority * 1_000_000 + int(task.available_at)
            self.client.zadd(self._agent_queue_key(task.agent), {task.id: score})
            
            # Also add to global queue for monitoring
            self.client.zadd("task_queue", {task.id: score})
            self.client.set(f"task:{task.id}:retry_count", 0)
        else:
            # In-memory fallback with agent-specific queues
            self.store[task.id] = task
            if task.agent not in self.agent_queues:
                self.agent_queues[task.agent] = []
            self.agent_queues[task.agent].append(task)
            # Keep agent queues sorted by priority
            self.agent_queues[task.agent].sort(key=lambda t: (t.priority, t.available_at))
            
        logger.info(
            "task enqueued"
            extra={"props": {"task_id": task.id, "agent": task.agent, "priority": task.priority}}
        )

    def dequeue(self, agent: str) -> Optional[Task]:
        """Optimized dequeue using agent-specific sorted sets."""
        if self.client:
            # Use agent-specific queue for O(log N) performance
            agent_queue_key = self._agent_queue_key(agent)
            now = time.time()
            
            # Get tasks in priority order (lowest score first)
            task_ids = self.client.zrange(agent_queue_key, 0, 9)  # Check up to 10 tasks
            
            for task_id in task_ids:
                raw = self.client.get(f"task:{task_id}")
                if not raw:
                    # Clean up orphaned task ID
                    self.client.zrem(agent_queue_key, task_id)
                    self.client.zrem("task_queue", task_id)
                    continue
                    
                data = json.loads(raw)
                
                # Check if task is ready (available_at <= now)
                if data.get("available_at", 0) > now:
                    continue
                    
                # Check if task is still queued
                if data.get("state") == "queued":
                    # Atomically claim the task
                    data["state"] = "in_progress"
                    self.client.set(f"task:{task_id}", json.dumps(data))
                    
                    # Remove from queues
                    self.client.zrem(agent_queue_key, task_id)
                    self.client.zrem("task_queue", task_id)
                    
                    return Task(**data)
                else:
                    # Task is no longer queued, clean up
                    self.client.zrem(agent_queue_key, task_id)
                    
            return None
        else:
            # In-memory fallback with optimized agent queues
            now = time.time()
            agent_queue = self.agent_queues.get(agent, [])
            
            for i, task in enumerate(agent_queue):
                if task.state == "queued" and task.available_at <= now:
                    task.state = "in_progress"
                    # Remove from agent queue
                    agent_queue.pop(i)
                    return task
                    
            return None

    def get_agent_queue_length(self, agent: str) -> int:
        """Get the number of queued tasks for a specific agent."""
        if self.client:
            return self.client.zcard(self._agent_queue_key(agent))
        else:
            return len([t for t in self.agent_queues.get(agent, []) if t.state == "queued"])

    def get_agent_queue_stats(self, agent: str) -> Dict[str, int]:
        """Get detailed queue statistics for an agent."""
        stats = {"queued": 0, "high_priority": 0, "medium_priority": 0, "low_priority": 0}
        
        if self.client:
            agent_queue_key = self._agent_queue_key(agent)
            task_ids = self.client.zrange(agent_queue_key, 0, -1)
            
            for task_id in task_ids:
                raw = self.client.get(f"task:{task_id}")
                if raw:
                    data = json.loads(raw)
                    if data.get("state") == "queued":
                        stats["queued"] += 1
                        priority = data.get("priority", 0)
                        if priority <= 1:
                            stats["high_priority"] += 1
                        elif priority <= 3:
                            stats["medium_priority"] += 1
                        else:
                            stats["low_priority"] += 1
        else:
            for task in self.agent_queues.get(agent, []):
                if task.state == "queued":
                    stats["queued"] += 1
                    if task.priority <= 1:
                        stats["high_priority"] += 1
                    elif task.priority <= 3:
                        stats["medium_priority"] += 1
                    else:
                        stats["low_priority"] += 1
                        
        return stats

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        if self.client:
            keys = self.client.keys("task:*")
            # Use pipeline for better performance
            if keys:
                pipe = self.client.pipeline()
                for key in keys:
                    pipe.get(key)
                items = [json.loads(item) for item in pipe.execute() if item]
            else:
                items = []
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
                "task failed"
                extra={"props": {"task_id": task_id, "retries": task.retries}}
            )
            return
        delay = min(self.base_delay * 2 ** (task.retries - 1), 60)
        task.state = "queued"
        task.priority += 1  # Increase priority for retries
        task.available_at = time.time() + delay
        
        if self.client:
            self.client.set(f"task:{task_id}", json.dumps(task.__dict__))
            score = task.priority * 1_000_000 + int(task.available_at)
            # Re-add to both queues
            self.client.zadd(self._agent_queue_key(task.agent), {task_id: score})
            self.client.zadd("task_queue", {task_id: score})
            self.client.set(f"task:{task_id}:retry_count", task.retries)
        else:
            self.store[task_id] = task
            # Re-add to agent queue and re-sort
            if task.agent not in self.agent_queues:
                self.agent_queues[task.agent] = []
            self.agent_queues[task.agent].append(task)
            self.agent_queues[task.agent].sort(key=lambda t: (t.priority, t.available_at))
            
        logger.info(
            "task retry"
            extra={"props": {"task_id": task_id, "attempt": task.retries, "delay": delay}}
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

    def get(self, task_id: str) -> Optional[Task]:
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

    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up old completed/failed tasks to prevent memory bloat."""
        if not self.client:
            return 0
            
        logger = logging.getLogger(__name__)
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned = 0
        
        # Get all task keys
        task_keys = self.client.keys("task:*")
        
        for key in task_keys:
            if ":retry_count" in key or ":error_log" in key:
                continue
                
            raw = self.client.get(key)
            if raw:
                data = json.loads(raw)
                if (data.get("state") in ["completed", "failed"] and 
                    data.get("available_at", 0) < cutoff_time):
                    
                    task_id = key.split(":", 1)[1]
                    # Remove from all data structures
                    self.client.delete(key)
                    self.client.delete(f"task:{task_id}:retry_count")
                    self.client.delete(f"task:{task_id}:error_log")
                    self.client.zrem("task_queue", task_id)
                    
                    # Remove from agent queue if present
                    agent = data.get("agent")
                    if agent:
                        self.client.zrem(self._agent_queue_key(agent), task_id)
                    
                    cleaned += 1
                    
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} old completed/failed tasks")
            
        return cleaned


queue = TaskQueue()
