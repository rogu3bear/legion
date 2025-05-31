"""
StateManager: Centralized state management for Legion.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class StateManager:
    """Manages centralized state, task logs, and feedback for Legion."""

    def __init__(self, state_dir: str = "./memory/state") -> None:
        """Initialize state directory, files, and default config."""
        logger.info("Initializing StateManager", extra={"state_dir": state_dir})
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "state.json"
        self.task_log = self.state_dir / "tasks.jsonl"
        self.error_log = self.state_dir / "errors.jsonl"
        self.feedback_log = self.state_dir / "feedback.jsonl"

        # Initialize state if not exists
        if not self.state_file.exists():
            self._save_state(
                {
                    "config": {
                        "confidence_threshold": 0.5,
                        "max_history": 100,
                        "assessment_interval": 600,
                    },
                    "metrics": {},
                    "agent_states": {},
                }
            )

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save state to JSON file."""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        if not self.state_file.exists():
            return {}
        with open(self.state_file) as f:
            return json.load(f)

    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update state with new values."""
        state = self.get_state()
        state.update(updates)
        self._save_state(state)

    def log_task(self, task: Dict[str, Any]) -> None:
        """Append task to task log."""
        task["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.task_log, "a") as f:
            f.write(json.dumps(task) + "\n")

    def log_error(self, error: Dict[str, Any]) -> None:
        """Append error to error log."""
        error["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.error_log, "a") as f:
            f.write(json.dumps(error) + "\n")

    def add_feedback(self, feedback: Dict[str, Any]) -> None:
        """Add feedback entry."""
        feedback["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.feedback_log, "a") as f:
            f.write(json.dumps(feedback) + "\n")

    def adjust_confidence_threshold(self, new_threshold: float) -> None:
        """Adjust confidence threshold in config."""
        state = self.get_state()
        state["config"]["confidence_threshold"] = new_threshold
        self._save_state(state)

    def get_recent_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent tasks from log."""
        tasks = []
        if self.task_log.exists():
            with open(self.task_log) as f:
                for line in f:
                    tasks.append(json.loads(line))
                    if len(tasks) >= limit:
                        break
        return tasks[::-1]  # Most recent first

    def get_recent_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent errors from log."""
        errors = []
        if self.error_log.exists():
            with open(self.error_log) as f:
                for line in f:
                    errors.append(json.loads(line))
                    if len(errors) >= limit:
                        break
        return errors[::-1]  # Most recent first

    def log_telemetry(self, event: Dict[str, Any]) -> None:
        """Append a telemetry event to the task log (or a dedicated telemetry log if desired)."""
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        event["type"] = event.get("type", "telemetry")
        with open(self.task_log, "a") as f:
            f.write(json.dumps(event) + "\n")


def save_agent_state_to_redis(redis_conn: Any) -> None:
    """Persist all active agents to Redis as JSON."""
    from interface.db.session import SessionLocal
    from interface.models.agent import Agent

    session = SessionLocal()
    try:
        agents = session.query(Agent).filter(Agent.is_active.is_(True)).all()
        for agent in agents:
            data = {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "model": agent.model,
                "temperature": agent.temperature,
                "max_tokens": agent.max_tokens,
                "is_active": agent.is_active,
                "config": agent.config,
                "created_at": agent.created_at.isoformat()
                if agent.created_at
                else None,
                "last_active": agent.last_active.isoformat()
                if agent.last_active
                else None,
            }
            redis_conn.set(
                f"legion:agents:{agent.id}",
                json.dumps(data),
                ex=86400,
            )
    finally:
        session.close()


def restore_agent_state_from_redis(redis_conn: Any) -> list[int]:
    """Load agent state from Redis back into the database."""
    from interface.db.session import SessionLocal
    from interface.models.agent import Agent

    session = SessionLocal()
    restored: list[int] = []
    try:
        keys = redis_conn.keys("legion:agents:*")
        for key in keys:
            raw = redis_conn.get(key)
            if not raw:
                continue
            data = json.loads(raw)
            agent = session.get(Agent, data["id"])
            if agent is None:
                agent = Agent(id=data["id"], name=data["name"], model=data["model"])
            agent.description = data.get("description")
            agent.temperature = data.get("temperature", 0.0)
            agent.max_tokens = data.get("max_tokens", 0)
            agent.is_active = data.get("is_active", True)
            agent.config = data.get("config")
            if data.get("created_at"):
                agent.created_at = datetime.fromisoformat(data["created_at"])
            if data.get("last_active"):
                agent.last_active = datetime.fromisoformat(data["last_active"])
            session.add(agent)
            restored.append(agent.id)
        session.commit()
    finally:
        session.close()
    return restored
