"""Lightweight agent registration store using Redis."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    import redis
except Exception:  # pragma: no cover
    redis = None


class _MemoryRedis:
    """Very small subset of Redis used for tests when real client is absent."""

    def __init__(self) -> None:
        self.store = {}

    def hset(self, name: str, mapping: dict) -> None:
        self.store.setdefault(name, {}).update(mapping)

    def hgetall(self, name: str) -> dict:
        return dict(self.store.get(name, {}))


class StateRepo:
    def __init__(self, r: Optional[Any] = None) -> None:
        if r is not None:
            self.r = r
        else:
            if redis is None:
                self.r = _MemoryRedis()
            else:
                self.r = redis.StrictRedis(decode_responses=True)

    def register_agent(self, agent_id: str, role: str, caps: list[str]) -> str:
        token = str(uuid.uuid4())
        data = {
            "id": agent_id,
            "role": role,
            "caps": json.dumps(caps),
            "token": token,
            "ts": int(time.time()),
        }
        self.r.hset(f"agents:{agent_id}", mapping=data)
        return token

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        data = self.r.hgetall(f"agents:{agent_id}")
        if not data:
            return None
        data["caps"] = json.loads(data.get("caps", "[]"))
        return data

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        data = self.get_agent(agent_id)
        if not data:
            return None
        ts = int(data.get("ts", 0))
        data["up_time"] = int(time.time()) - ts
        return data


repo = StateRepo()
