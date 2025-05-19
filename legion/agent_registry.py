"""Utilities for managing Legion's agent registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AgentMeta:
    """Metadata describing an agent's runtime configuration."""

    name: str
    function_tags: List[str]
    priority: int
    status_route: str
    max_retries: int = 0
    cooldown: int = 0


_REGISTRY_PATH = Path(__file__).resolve().parent / "registry" / "agent_registry.json"


class AgentRegistry:
    """Simple loader for agent metadata."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _REGISTRY_PATH
        self._agents: Dict[str, AgentMeta] = {}
        self.load()

    def load(self) -> None:
        """Load registry metadata from disk."""
        if not self.path.exists():
            raise FileNotFoundError(f"Registry file missing: {self.path}")
        data = json.loads(self.path.read_text())
        self._agents = {}
        for name, conf in data.items():
            self._agents[name] = AgentMeta(name=name, **conf)

    def get(self, name: str) -> Optional[AgentMeta]:
        return self._agents.get(name)

    def all(self) -> Dict[str, AgentMeta]:
        return dict(self._agents)


registry = AgentRegistry()
