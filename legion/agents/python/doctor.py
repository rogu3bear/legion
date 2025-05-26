from __future__ import annotations

"""DoctorAgent implementation for diagnostics and remediation."""

import json
import os
from datetime import datetime, timezone

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

import yaml

from legion.agents.base import BaseAgent


class DoctorAgent(BaseAgent):
    """Agent responsible for diagnosing issues and suggesting remedies."""

    def __init__(self, name: str, config: dict | None = None, llm_client=None) -> None:
        super().__init__(name, config or {}, llm_client)
        self.redis = None

    def setup(self, orchestrator) -> None:
        """Load configuration and register with the orchestrator."""
        self.orchestrator = orchestrator
        cfg_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "configs", "doctor.yaml"
        )
        try:
            with open(cfg_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.config.update(data)
        except FileNotFoundError:
            pass
        if redis is not None:
            try:
                port = int(os.getenv("REDIS_PORT", 7810))
                self.redis = redis.Redis(
                    host="localhost", port=port, decode_responses=True
                )
            except Exception:  # pragma: no cover - redis unavailable
                self.redis = None
        if orchestrator:
            try:
                orchestrator.register_agent(
                    self.name, "doctor", ["diagnose_issue", "suggest_remedy"]
                )
            except Exception:  # pragma: no cover - registration failure
                pass

    def _log_diagnosis(
        self, symptoms: dict[str, str], diagnosis: dict[str, str]
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symptoms": symptoms,
            "diagnosis": diagnosis,
        }
        if self.redis:
            try:
                self.redis.rpush("doctor:diagnosis_log", json.dumps(entry))
            except Exception:  # pragma: no cover - redis errors
                pass

    def process_message(self, msg: dict[str, any], ctx: dict | None = None):
        """Dispatch message based on requested action."""
        action = msg.get("action")
        if action == "diagnose":
            diagnosis = self.diagnose_issue(msg.get("symptoms", {}))
            self._log_diagnosis(msg.get("symptoms", {}), diagnosis)
            return diagnosis
        if action == "remedy":
            return self.suggest_remedy(msg.get("diagnosis", {}))
        raise ValueError("Unknown action")

    def diagnose_issue(self, symptoms: dict[str, str]) -> dict[str, str]:
        """Return a structured diagnosis based on provided symptoms."""
        error = symptoms.get("error", "").lower()
        if error == "cpu_high":
            return {"issue": "High CPU Usage", "severity": "critical"}
        if error == "memory_leak":
            return {"issue": "Memory Leak", "severity": "high"}
        return {"issue": "Unknown", "severity": "unknown"}

    def suggest_remedy(self, diagnosis: dict[str, str]) -> list[str]:
        """Map a diagnosis to a list of remedies."""
        mapping = {
            "High CPU Usage": ["Scale service", "Optimize code"],
            "Memory Leak": ["Restart process", "Check logs"],
            "Unknown": ["Gather more diagnostics"],
        }
        return mapping.get(diagnosis.get("issue"), ["No remedy found"])
