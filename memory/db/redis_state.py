"""Helper for conversation caching in Redis."""
from __future__ import annotations

import json
from typing import Any

try:  # pragma: no cover - optional dependency
    import redis  # type: ignore
except Exception:  # pragma: no cover - Redis not installed
    redis = None


class ConversationCache:
    """Simple get/set wrapper for conversation data."""

    KEY_PREFIX = "conversation:"

    def __init__(self, r: Any | None = None) -> None:
        if r is not None:
            self.r = r
        else:
            if redis is None:
                raise RuntimeError("Redis library not available")
            self.r = redis.StrictRedis(decode_responses=True)

    def set(self, conv_id: str, data: dict[str, Any]) -> None:
        self.r.set(f"{self.KEY_PREFIX}{conv_id}", json.dumps(data))

    def get(self, conv_id: str) -> dict[str, Any] | None:
        raw = self.r.get(f"{self.KEY_PREFIX}{conv_id}")
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None


def get_conversation(conv_id: str, cache: ConversationCache | None = None) -> dict[str, Any] | None:
    cache = cache or ConversationCache()
    return cache.get(conv_id)


def set_conversation(conv_id: str, data: dict[str, Any], cache: ConversationCache | None = None) -> None:
    cache = cache or ConversationCache()
    cache.set(conv_id, data)
