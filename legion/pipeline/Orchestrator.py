from __future__ import annotations

# ruff: noqa: N999
from typing import ClassVar

from .BaseAgent import BaseAgent
from .MetricsAgent import MetricsAgent
from .schemas import AgentResponse, InternalRequest
from .TherapistAgent import TherapistAgent


class Orchestrator:
    """Simple orchestrator routing requests to agents."""

    _agents: ClassVar[dict[str, BaseAgent]] = {}
    _registry: ClassVar[dict[str, type[BaseAgent]]] = {
        "metrics": MetricsAgent,
    }

    @classmethod
    def dispatch(cls, request: InternalRequest) -> AgentResponse:
        """Validate via therapist and route to the requested agent."""
        TherapistAgent.validate(request)
        agent = cls.get_agent_by_key(request.agent_key)
        response = agent.process(request)
        cls.send_response(response, request.channel)
        return response

    @classmethod
    def get_agent_by_key(cls, key: str) -> BaseAgent:
        if key not in cls._agents:
            agent_cls = cls._registry.get(key)
            if agent_cls is None:
                raise ValueError(f"unknown agent {key}")
            cls._agents[key] = agent_cls()
        return cls._agents[key]

    @staticmethod
    def send_response(response: AgentResponse, channel: str) -> None:
        from .DiscordAdapter import DiscordAdapter  # Local import to avoid cycle

        DiscordAdapter.send_message(channel, response.text)
