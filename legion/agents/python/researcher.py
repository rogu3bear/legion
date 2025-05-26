from __future__ import annotations

"""ResearcherAgent implementation for search and synthesis."""

import json
import os
from hashlib import sha256

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

import yaml

from legion.agents.base import BaseAgent
from skills.search import search_web
from skills.summarize import summarize_texts


class ResearcherAgent(BaseAgent):
    """Agent that conducts research and synthesizes findings."""

    def __init__(self, name: str, config: dict | None = None, llm_client=None) -> None:
        super().__init__(name, config or {}, llm_client)
        self.redis = None

    def setup(self, orchestrator) -> None:
        """Prepare utilities and register with orchestrator."""
        self.orchestrator = orchestrator
        cfg_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "researcher.yaml")
        try:
            with open(cfg_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.config.update(data)
        except FileNotFoundError:
            pass
        if redis is not None:
            try:
                port = int(os.getenv("REDIS_PORT", 7810))
                self.redis = redis.Redis(host="localhost", port=port, decode_responses=True)
            except Exception:  # pragma: no cover - redis unavailable
                self.redis = None
        if orchestrator:
            try:
                orchestrator.register_agent(self.name, "researcher", ["conduct_research", "synthesize_findings"])
            except Exception:  # pragma: no cover - registration failure
                pass

    def _cache_key(self, query: str) -> str:
        return "research_cache:" + sha256(query.encode("utf-8")).hexdigest()

    def conduct_research(self, query: str, sources: list[str]) -> list[str]:
        """Search the web and return raw data, using Redis cache when available."""
        key = self._cache_key(query)
        if self.redis:
            try:
                cached = self.redis.get(key)
                if cached:
                    return json.loads(cached)
            except Exception:  # pragma: no cover - redis errors
                pass
        data = search_web(query, sources)
        if self.redis:
            try:
                self.redis.setex(key, 86400, json.dumps(data))
            except Exception:  # pragma: no cover - redis errors
                pass
        return data

    def synthesize_findings(self, raw_data: list[str]) -> str:
        """Synthesize raw search data into a report."""
        return summarize_texts(raw_data)

    def process_message(self, msg: dict[str, any], ctx: dict | None = None):
        """Dispatch message to research or synthesis handlers."""
        action = msg.get("action")
        if action == "research":
            return self.conduct_research(msg.get("query", ""), msg.get("sources", []))
        if action == "synthesize":
            return self.synthesize_findings(msg.get("raw_data", []))
        raise ValueError("Unknown action")
