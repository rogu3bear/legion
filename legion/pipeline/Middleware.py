from __future__ import annotations

# ruff: noqa: N999
from datetime import datetime

from .Orchestrator import Orchestrator
from .schemas import InternalRequest


class Middleware:
    """Sequential request middleware chain."""

    @staticmethod
    def authenticate(request: InternalRequest) -> None:
        """Verify the user has permissions to run the command."""
        # TODO: implement real authentication rules
        if not request.user_id:
            raise PermissionError("anonymous access denied")

    @staticmethod
    def enrich_context(request: InternalRequest) -> None:
        """Add context metadata to the request args."""
        request.args["received_at"] = datetime.utcnow().isoformat()

    @staticmethod
    def rate_limit(request: InternalRequest) -> None:
        """Enforce simple rate limits per user (placeholder)."""
        # TODO: integrate rate limit store
        _ = request

    @staticmethod
    def process(request: InternalRequest) -> None:
        """Run middleware steps then dispatch to orchestrator."""
        Middleware.authenticate(request)
        Middleware.enrich_context(request)
        Middleware.rate_limit(request)
        Orchestrator.dispatch(request)
