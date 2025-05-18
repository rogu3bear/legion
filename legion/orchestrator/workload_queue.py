from __future__ import annotations

import time
import threading
from typing import Any, Dict, List, Optional

from .state_repo import repo, StateRepo


class WorkloadQueue:
    """FIFO queue with simple priority support."""

    def __init__(self, repo: StateRepo) -> None:
        self.repo = repo
        self._lock = threading.Lock()

    def enqueue(self, task: Dict[str, Any]) -> None:
        """Add a task to the queue."""
        task.setdefault("priority", 0)
        task.setdefault("state", "pending")
        task.setdefault("created", time.time())
        with self._lock:
            q = self.repo.get_queue()
            q.append(task)
            self.repo.set_queue(q)

    def dequeue(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Return next task for an agent, or None if queue empty."""
        with self._lock:
            q = sorted(
                self.repo.get_queue(), key=lambda t: (t.get("priority", 0), t.get("created", 0))
            )
            if not q:
                return None
            task = q.pop(0)
            task["state"] = "assigned"
            task["agent_id"] = agent_id
            self.repo.set_queue(q)
            self.repo.record_agent_task(agent_id, task)
            return task

    def peek(self) -> Optional[Dict[str, Any]]:
        """Peek at the next task without removing it."""
        with self._lock:
            q = sorted(
                self.repo.get_queue(), key=lambda t: (t.get("priority", 0), t.get("created", 0))
            )
            return q[0] if q else None

    def summary(self) -> Dict[str, int]:
        """Return counts grouped by priority and state."""
        counts: Dict[str, int] = {}
        with self._lock:
            for item in self.repo.get_queue():
                key = f"P{item.get('priority',0)}-{item.get('state','pending')}"
                counts[key] = counts.get(key, 0) + 1
        return counts


queue = WorkloadQueue(repo)
