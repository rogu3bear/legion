"""Lightweight agent registration store using Redis."""

from __future__ import annotations

import hmac
import json
import secrets
import time
import uuid
from typing import Any

try:  # pragma: no cover - optional dependency
    import redis
except Exception:  # pragma: no cover
    redis = None


class _MemoryRedis:
    """Very small subset of Redis used for tests when real client is absent."""

    def __init__(self) -> None:
        self.store = {}
        self.values = {}

    def hset(self, name: str, mapping: dict) -> None:
        self.store.setdefault(name, {}).update(mapping)

    def hgetall(self, name: str) -> dict:
        return dict(self.store.get(name, {}))

    def set(self, key: str, value: str) -> None:
        self.values[key] = value

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def delete(self, key: str) -> None:
        self.values.pop(key, None)


class StateRepo:
    def __init__(self, r: Any | None = None) -> None:
        if r is not None:
            self.r = r
        else:
            if redis is None:
                self.r = _MemoryRedis()
            else:
                self.r = redis.StrictRedis(decode_responses=True)

    # -- Agent Registration Handshake --
    def initiate_handshake(
        self, agent_id: str, role: str, caps: list[str]
    ) -> dict[str, str]:
        """Begin registration handshake and return challenge token."""
        challenge = secrets.token_hex(16)
        token = str(uuid.uuid4())
        data = {
            "id": agent_id,
            "role": role,
            "caps": json.dumps(caps),
            "challenge": challenge,
            "token": token,
            "ts": int(time.time()),
        }
        self.r.hset(f"handshake:{agent_id}", mapping=data)
        return {"challenge_token": challenge}

    def complete_handshake(
        self, agent_id: str, signed_challenge: str, secret: str
    ) -> str:
        """Finalize handshake and persist agent record."""
        record = self.r.hgetall(f"handshake:{agent_id}")
        if not record:
            raise ValueError("handshake not initiated")
        challenge = record.get("challenge")
        expected = hmac.new(secret.encode(), challenge.encode(), "sha256").hexdigest()
        if not hmac.compare_digest(signed_challenge, expected):
            raise ValueError("unauthorized")
        agent_data = {
            "id": record["id"],
            "role": record["role"],
            "caps": record["caps"],
            "token": record["token"],
            "ts": record["ts"],
        }
        self.r.hset(f"agents:{agent_id}", mapping=agent_data)
        self.r.delete(f"handshake:{agent_id}")
        return record["token"]

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

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        data = self.r.hgetall(f"agents:{agent_id}")
        if not data:
            return None
        data["caps"] = json.loads(data.get("caps", "[]"))
        return data

    def get_agent_status(self, agent_id: str) -> dict[str, Any] | None:
        data = self.get_agent(agent_id)
        if not data:
            return None
        ts = int(data.get("ts", 0))
        data["up_time"] = int(time.time()) - ts
        return data


repo = StateRepo()
