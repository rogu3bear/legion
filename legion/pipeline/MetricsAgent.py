from __future__ import annotations

# ruff: noqa: N999
from typing import Any

from .BaseAgent import BaseAgent
from .schemas import InternalRequest


class MetricsAgent(BaseAgent):
    """Example agent implementation for metrics collection."""

    def validate_payload(self, args: dict[str, Any]) -> None:
        # TODO: expand argument validation rules
        if "action" not in args:
            raise ValueError("metrics 'action' missing")

    def perform_task(self, request: InternalRequest, context: list[Any]) -> Any:
        # Stub metrics gathering based on the action
        action = request.args.get("action")
        if action == "healthcheck":
            return {"status": "ok"}
        return {"action": action, "detail": "no-op"}

    def build_response(self, result: Any) -> str:
        return str(result)
