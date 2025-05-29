"""Assurance gate decorator."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)


def assurance_gate(threshold: float = 0.85) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Annotate a function with an assurance threshold."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper.__assurance__ = threshold
        logger.debug("assurance_gate %.2f applied to %s", threshold, func.__name__)
        return wrapper

    return decorator
