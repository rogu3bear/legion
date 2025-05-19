from __future__ import annotations

# ruff: noqa: N999
from .schemas import InternalRequest


class TherapistAgent:
    """Gatekeeping validation before an agent processes a request."""

    @staticmethod
    def validate(request: InternalRequest) -> None:
        """Raise an exception if the request fails therapist checks."""
        if not request.command:
            raise ValueError("command missing")
        banned = {"shutdown", "rm -rf"}
        text = str(request.args.get("raw", "")).lower()
        for word in banned:
            if word in text:
                raise ValueError("unsafe command detected")
