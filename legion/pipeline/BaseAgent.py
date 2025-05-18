from __future__ import annotations

# ruff: noqa: N999
from typing import Any

from .schemas import AgentResponse, InternalRequest


class BaseAgent:
    """Base class for all agents in the simplified pipeline."""

    def process(self, request: InternalRequest) -> AgentResponse:
        """Run full processing pipeline for a request."""
        self.validate_payload(request.args)
        context = self.retrieve_memories(request.user_id)
        result = self.perform_task(request, context)
        self.store_memories(request.user_id, result)
        response_text = self.build_response(result)
        return AgentResponse(text=response_text)

    # -- Methods to implement in subclasses --
    def validate_payload(self, args: dict[str, Any]) -> None:
        raise NotImplementedError

    def perform_task(self, request: InternalRequest, context: list[Any]) -> Any:
        raise NotImplementedError

    def retrieve_memories(self, user_id: str) -> list[Any]:
        return []

    def store_memories(self, user_id: str, result: Any) -> None:
        pass

    def build_response(self, result: Any) -> str:
        raise NotImplementedError
