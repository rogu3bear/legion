from __future__ import annotations
"""Researcher agent stub.

Author: Codex
"""

from legion.agents.base import BaseAgent


class ResearcherAgent(BaseAgent):
    """Agent that performs research tasks."""

    def __init__(self, name: str, config: dict, llm_client=None):
        super().__init__(name, config, llm_client)

    async def gather_sources(self, topic: str) -> list[str]:
        """Return list of sources for topic (stub)."""
        if not topic:
            return []
        query = topic.replace(" ", "+")
        return [f"https://example.com/search?q={query}"]
