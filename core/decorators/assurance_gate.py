"""Simple assurance gate decorator."""

from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable


DEFAULT_THRESHOLD = 0.85


def assurance_gate(threshold: float = DEFAULT_THRESHOLD) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Basic assurance gate enforcing a confidence threshold."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_coro = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)
            if isinstance(result, dict) and result.get("confidence", 1.0) < threshold:
                return {"error": "assurance-failed", "confidence": result.get("confidence", 0.0)}
            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            if isinstance(result, dict) and result.get("confidence", 1.0) < threshold:
                return {"error": "assurance-failed", "confidence": result.get("confidence", 0.0)}
            return result

        return async_wrapper if is_coro else sync_wrapper

    return decorator
