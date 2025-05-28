#!/usr/bin/env python3
"""Add tag_context and task_owner fields to stored task JSON objects in Redis."""

import json
import os
from typing import Any

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - redis not installed
    redis = None


class FakeRedis:
    def __init__(self):
        self.store = {}

    def keys(self, pattern: str):
        import fnmatch
        return [k for k in self.store if fnmatch.fnmatch(k, pattern)]

    def get(self, key: str) -> Any:
        return self.store.get(key)

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value


def get_client():
    port = int(os.getenv("REDIS_PORT", 7600))
    if redis is None:
        return FakeRedis()
    return redis.Redis(host="localhost", port=port, decode_responses=True)


def migrate(client) -> None:
    for key in client.keys("task:*"):
        raw = client.get(key)
        if raw is None:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        data.setdefault("tag_context", "")
        data.setdefault("task_owner", "")
        client.set(key, json.dumps(data))


def main():
    client = get_client()
    migrate(client)


if __name__ == "__main__":
    main()
