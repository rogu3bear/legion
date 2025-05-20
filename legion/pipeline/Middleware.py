from __future__ import annotations

import time

# ruff: noqa: N999
from datetime import datetime
from typing import Dict, Set, Tuple

from .Orchestrator import Orchestrator
from .schemas import InternalRequest


class Middleware:
    """Sequential request middleware chain."""

    # Simple in-memory rate limit tracking
    _rate_limits: Dict[
        str, Tuple[int, float]
    ] = {}  # {user_id: (count, first_request_time)}
    _max_requests_per_minute = 30
    _authenticated_users: Set[str] = set()  # Normally this would come from a database

    @staticmethod
    def authenticate(request: InternalRequest) -> None:
        """
        Verify the user has permissions to run the command.

        Args:
            request: The internal request to validate.

        Raises:
            PermissionError: If the user doesn't have the required permissions.
        """
        if not request.user_id:
            raise PermissionError("Anonymous access denied")

        # Normally this would check against a database or auth service
        # For implementation example:
        if request.command in [
            "admin",
            "system",
            "manage_agents",
        ] and request.user_id not in ["admin", "system"]:
            raise PermissionError(
                f"User {request.user_id} lacks permission for {request.command}"
            )

        # Consider request authenticated
        Middleware._authenticated_users.add(request.user_id)

    @staticmethod
    def enrich_context(request: InternalRequest) -> None:
        """Add context metadata to the request args."""
        current_time = datetime.utcnow()
        request.args["received_at"] = current_time.isoformat()
        request.args["metadata"] = {
            "is_authenticated": request.user_id in Middleware._authenticated_users,
            "agent_key": request.agent_key,
            "channel": request.channel,
        }

    @staticmethod
    def rate_limit(request: InternalRequest) -> None:
        """
        Enforce rate limits per user based on a sliding window.

        Args:
            request: The internal request to rate limit.

        Raises:
            ValueError: If the user has exceeded their rate limit.
        """
        user_id = request.user_id
        current_time = time.time()

        # Get current rate limit info for user or initialize
        count, first_request_time = Middleware._rate_limits.get(
            user_id, (0, current_time)
        )

        # Reset rate limit if one minute has passed since first request
        if current_time - first_request_time > 60:
            count = 0
            first_request_time = current_time

        # Increment counter
        count += 1

        # Check if rate limit exceeded
        if count > Middleware._max_requests_per_minute:
            wait_time = 60 - (current_time - first_request_time)
            raise ValueError(
                f"Rate limit exceeded. Try again in {wait_time:.1f} seconds."
            )

        # Store updated rate limit data
        Middleware._rate_limits[user_id] = (count, first_request_time)

    @staticmethod
    def process(request: InternalRequest) -> None:
        """Run middleware steps then dispatch to orchestrator."""
        Middleware.authenticate(request)
        Middleware.enrich_context(request)
        Middleware.rate_limit(request)
        Orchestrator.dispatch(request)
