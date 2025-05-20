from __future__ import annotations

# ruff: noqa: N999
from typing import Dict, List, Set

from .schemas import InternalRequest


class TherapistAgent:
    """Gatekeeping validation before an agent processes a request."""

    # Configurable directive rules
    _blocked_directives: Set[str] = {
        "SYSTEM_SHUTDOWN",
        "FACTORY_RESET",
        "DELETE_ALL_DATA",
    }
    _sensitive_commands: Set[str] = {"admin", "delete", "purge", "modify_system"}
    _restricted_agent_commands: Dict[str, List[str]] = {
        "metrics": ["collect", "analyze", "report"],
        "doctor": ["diagnose", "heal", "prescribe"],
        "architect": ["design", "plan", "review"],
    }

    @staticmethod
    def validate(request: InternalRequest) -> None:
        """
        Raise an exception if the request fails therapist checks.

        Args:
            request: The internal request to validate.

        Raises:
            ValueError: If the request is invalid or violates security rules.
            PermissionError: If the request attempts to access forbidden functionality.
        """
        # Basic validation
        if not request.command:
            raise ValueError("Command missing in request")

        # Check for blocked directives in args
        args_str = str(request.args).lower()
        for directive in TherapistAgent._blocked_directives:
            if directive.lower() in args_str:
                raise PermissionError(f"Blocked directive detected: {directive}")

        # Agent-specific command validation
        if (
            request.agent_key in TherapistAgent._restricted_agent_commands
            and request.command
            not in TherapistAgent._restricted_agent_commands[request.agent_key]
        ):
            allowed = ", ".join(
                TherapistAgent._restricted_agent_commands[request.agent_key]
            )
            raise ValueError(
                f"Agent '{request.agent_key}' cannot process command '{request.command}'. "
                f"Allowed commands: {allowed}"
            )

        # Sensitive command validation
        if request.command in TherapistAgent._sensitive_commands:
            # Check for additional authentication or confirmation
            if not request.args.get("confirm") and not request.args.get(
                "authorization_token"
            ):
                raise PermissionError(
                    f"Sensitive command '{request.command}' requires confirmation or authorization"
                )

        # Content safety checks for text
        if "text" in request.args:
            text = request.args["text"]
            if isinstance(text, str):
                unsafe_terms = TherapistAgent._check_content_safety(text)
                if unsafe_terms:
                    terms_str = ", ".join(unsafe_terms)
                    raise ValueError(f"Content safety violation detected: {terms_str}")

    @staticmethod
    def _check_content_safety(text: str) -> List[str]:
        """
        Check text content for safety violations.

        Args:
            text: The text to check.

        Returns:
            List of detected unsafe terms (empty if safe).
        """
        # This is a very simple implementation
        # A real system would use more sophisticated content moderation
        unsafe_terms = []
        safety_triggers = [
            "hack the system",
            "bypass security",
            "override restrictions",
            "delete all data",
            "factory reset",
            "system shutdown",
        ]

        text_lower = text.lower()
        for term in safety_triggers:
            if term in text_lower:
                unsafe_terms.append(term)

        return unsafe_terms
