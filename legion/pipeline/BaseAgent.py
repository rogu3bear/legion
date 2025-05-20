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
        """
        Validate the incoming payload for required fields and correct data types.

        Args:
            args: Dictionary of arguments passed to the agent.

        Raises:
            ValueError: If the payload is invalid or missing required fields.
        """
        # Base implementation performs no validation
        # Subclasses should override this method to implement specific validation logic
        pass

    def perform_task(self, request: InternalRequest, context: list[Any]) -> Any:
        """
        Execute the agent's primary functionality using the request and context.

        Args:
            request: The full internal request object.
            context: Any retrieved memories or context for this user.

        Returns:
            Any result data needed for response building.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement perform_task()")

    def retrieve_memories(self, user_id: str) -> list[Any]:
        """
        Retrieve stored memories or context for the specified user.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            A list of memory items for the user (empty list by default).
        """
        return []

    def store_memories(self, user_id: str, result: Any) -> None:
        """
        Store results from task execution as memories for future context.

        Args:
            user_id: Unique identifier for the user.
            result: The data to store as a memory.
        """
        pass

    def build_response(self, result: Any) -> str:
        """
        Convert the task result into a formatted response string.

        Args:
            result: The result from perform_task().

        Returns:
            A formatted string response to return to the user.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement build_response()")
