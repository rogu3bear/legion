import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class StateRepo:
    """Simple persistent repository for agents and tasks."""

    def __init__(self, path: str = "memory/state/repo.json") -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self._data: Dict[str, Any] = {"agents": {}, "tasks": {}, "queue": []}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            with open(self.path) as f:
                self._data = json.load(f)
        else:
            self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2)

    # --- Agent management -------------------------------------------------
    def register_agent(self, agent_id: str, role: str, capabilities: List[str]) -> str:
        """Register an agent and return its auth token."""
        with self._lock:
            token = uuid4().hex
            self._data["agents"][agent_id] = {
                "id": agent_id,
                "role": role,
                "capabilities": capabilities,
                "token": token,
                "tasks": [],
            }
            self._save()
            return token

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._data["agents"].get(agent_id)

    def get_agent_tasks(self, agent_id: str) -> List[Dict[str, Any]]:
        agent = self._data["agents"].get(agent_id)
        if not agent:
            return []
        return [self._data["tasks"].get(tid) for tid in agent.get("tasks", []) if tid in self._data["tasks"]]

    def record_agent_task(self, agent_id: str, task: Dict[str, Any]) -> None:
        with self._lock:
            agent = self._data["agents"].setdefault(agent_id, {"tasks": []})
            agent.setdefault("tasks", []).append(task["id"])
            self._data["tasks"][task["id"]] = task
            self._save()

    # --- Queue persistence -----------------------------------------------
    def get_queue(self) -> List[Dict[str, Any]]:
        return list(self._data.get("queue", []))

    def set_queue(self, queue: List[Dict[str, Any]]) -> None:
        self._data["queue"] = queue
        self._save()


repo = StateRepo()
