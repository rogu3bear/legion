import logging
import os
import json
from fastapi import APIRouter, Response

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

logger = logging.getLogger(__name__)
router = APIRouter()


def get_redis_client() -> "redis.Redis | None":
    if redis is None:
        return None
    try:
        port = int(os.getenv("REDIS_PORT", 7810))
        return redis.Redis(host="localhost", port=port, decode_responses=True)
    except Exception:
        return None


@router.get("/", response_class=Response, summary="Prometheus metrics")
def metrics() -> Response:
    """Return system metrics in Prometheus exposition format."""
    client = get_redis_client()
    stats: dict[str, str] = {}
    if client is not None:
        try:
            stats = client.hgetall("metrics:latest") or {}
        except Exception:
            logger.exception("Failed reading metrics from Redis")
    lines = [
        "# HELP legion_tasks_total Total tasks processed",
        "# TYPE legion_tasks_total counter",
        f"legion_tasks_total {stats.get('legion_tasks_total', '0')}",
        "# HELP legion_agents_registered Current registered agents",
        "# TYPE legion_agents_registered gauge",
        f"legion_agents_registered {stats.get('legion_agents_registered', '0')}",
    ]
    for key, value in stats.items():
        if key in {"legion_tasks_total", "legion_agents_registered"}:
            continue
        lines.append(f"{key} {value}")
    body = "\n".join(lines) + "\n"
    return Response(content=body, media_type="text/plain")


@router.get("/summary", summary="Latest metrics summary")
def metrics_summary() -> dict:
    """Return the latest metrics JSON payload."""
    client = get_redis_client()
    if client is None:
        return {}
    try:
        raw = client.get("metrics:latest")
    except Exception:
        logger.exception("Failed reading metrics")
        return {}
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}
