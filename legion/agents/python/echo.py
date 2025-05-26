"""Echo agent implementation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from legion.agents.base import BaseAgent


class EchoAgent(BaseAgent):
    """Simple agent that mirrors incoming messages and persists a log."""

    system_prompt = (
        "You are \U0001f501 the Echo Agent—repeat back any message you receive, "
        "useful for diagnostics and testing message flow."
    )

    def __init__(self, orchestrator) -> None:
        super().__init__(orchestrator)
        self.log_buffer: list[dict[str, Any]] = []
        log_dir = Path("memory") / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / "echo_agent.jsonl"

    def _flush_buffer(self) -> None:
        if not self.log_buffer:
            return
        with open(self.log_file, "a", encoding="utf-8") as f:
            for entry in self.log_buffer:
                f.write(json.dumps(entry) + "\n")
        self.log_buffer.clear()

    async def handle_echo(self, message: str) -> str:
        """Echo the provided message and persist a structured log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
        }
        self.log_buffer.append(entry)
        if len(self.log_buffer) >= 10:
            self._flush_buffer()
        # Use BaseAgent's handle_message for consistency
        return await self.handle_message(
            content=message,
            author=self.name,
            timestamp=None,
        )

    def close(self) -> None:
        """Flush remaining logs when the agent is disposed."""
        self._flush_buffer()
