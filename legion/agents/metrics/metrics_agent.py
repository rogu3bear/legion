import json
import time
from typing import Any, Dict

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None


class MetricsAgent:
    KEY = "metrics:latest"

    def __init__(self, r: "redis.StrictRedis | None" = None) -> None:
        if r is not None:
            self.r = r
        else:
            self.r = redis.StrictRedis(decode_responses=True) if redis else None

    async def collect(self) -> None:
        if self.r is None:
            return
        # queue depth
        q_depth = self.r.zcard("queue:tasks")
        # agent heartbeats (age in seconds)
        agents: Dict[str, int] = {}
        for aid in self.r.smembers("agents:set"):
            ts = self.r.hget(f"agents:{aid}", "heartbeat_ts")
            if ts is not None:
                agents[aid] = int(time.time()) - int(ts)
        payload: Dict[str, Any] = {
            "ts": int(time.time()),
            "queue_depth": q_depth,
            "agent_heartbeat_age": agents,
        }
        self.r.set(self.KEY, json.dumps(payload))
