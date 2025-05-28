from __future__ import annotations

"""Therapist gate decorator for agent calls."""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable

from legion.task_queue import queue as task_queue

logger = logging.getLogger(__name__)

# Global flag to enable/disable therapist checks
ENABLED = True


def enable(flag: bool = True) -> None:
    """Enable or disable therapist guard globally."""
    global ENABLED
    ENABLED = flag


def therapist_guard(allowed_schema: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator enforcing therapist validation around agent calls."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_coro = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not ENABLED:
                return await func(*args, **kwargs)
            reason = _run_checks(args[0] if args else None, allowed_schema)
            if reason:
                logger.warning("Therapist blocked %s: %s", func.__name__, reason)
                return {"error": "Therapist-blocked", "reason": reason}
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not ENABLED:
                return func(*args, **kwargs)
            reason = _run_checks(args[0] if args else None, allowed_schema)
            if reason:
                logger.warning("Therapist blocked %s: %s", func.__name__, reason)
                return {"error": "Therapist-blocked", "reason": reason}
            return func(*args, **kwargs)

        return async_wrapper if is_coro else sync_wrapper

    return decorator


def _run_checks(agent: Any, allowed_schema: str) -> str | None:
    """Run simple validation checks."""
    # Check agent active flag
    if getattr(agent, "disabled", False):
        return "agent-disabled"

    # Workload queue sanity: block if >10 failed tasks
    try:
        summary = task_queue.summary()
        if summary.get("failed", 0) > 10:
            return "workload-queue-high-failures"
    except Exception as exc:  # noqa: BLE001
        logger.error("Queue summary failed: %s", exc)

    # Schema check placeholder
    if allowed_schema != "directive":
        return "schema-mismatch"

    return None


therapist_guard.enable = enable  # type: ignore[attr-defined]
