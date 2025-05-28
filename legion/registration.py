"""Agent registration handshake management."""

from __future__ import annotations

import hmac
import json
import logging
import os
import secrets
import time
from typing import Any, Dict

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None


class RegistrationService:
    """Handle agent registration handshake using Redis."""

    def __init__(self, host: str = "localhost", port: int = None, secret: str = "secret") -> None:
        self.host = host
        self.port = port if port is not None else int(os.getenv("REDIS_PORT", 7600))
        self.secret = secret
        if redis is None:
            self.client = None
            self.store: Dict[str, Any] = {}
            self.logs: list[str] = []
        else:
            self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def _log(self, payload: Dict[str, Any]) -> None:
        data = json.dumps(payload)
        if self.client:
            self.client.rpush("handshake_log", data)
        else:
            self.logs.append(data)

    def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        phase = payload.get("phase")
        if phase == "INITIAL_REQUEST":
            agent_id = payload.get("agent_id")
            if self.client:
                self.client.set(f"agent:{agent_id}:state", "init")
            challenge = secrets.token_hex(16)
            if self.client:
                self.client.set(f"agent:{agent_id}:challenge", challenge)
            self._log(payload)
            return {"challenge_token": challenge, "nonce": secrets.token_hex(8)}
        if phase == "AUTH_RESPONSE":
            agent_id = payload.get("agent_id")
            signed = payload.get("signed_challenge")
            challenge = None
            if self.client:
                challenge = self.client.get(f"agent:{agent_id}:challenge")
            if not challenge:
                return {"error": "no challenge"}
            expected = hmac.new(self.secret.encode(), challenge.encode(), "sha256").hexdigest()
            if signed != expected:
                self._log({"phase": "AUTH_RESPONSE", "status": "failed", "agent_id": agent_id})
                return {"error": "unauthorized"}
            if self.client:
                self.client.set(f"agent:{agent_id}:state", "ready")
            session_id = secrets.token_hex(8)
            self._log(payload)
            return {"status": "registered", "session_id": session_id, "ts": time.time()}
        return {"error": "invalid phase"}


service = RegistrationService()
