import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from interface.api.v1.endpoints.system import _call_orchestrator

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
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


class EchoPayload(BaseModel):
    message: str


@router.post("/", summary="Send message to Echo agent", response_model=Dict[str, str])
def send_echo(payload: EchoPayload) -> Dict[str, str]:
    """Proxy a message to the Echo agent via the orchestrator."""
    command_payload = {
        "agent_name": "echo_agent",
        "message": payload.message,
    }
    response = _call_orchestrator(
        action="dispatch_agent_message", payload=command_payload
    )
    content = response.get("response")
    if content is None:
        raise HTTPException(status_code=502, detail="No response from orchestrator")
    return {"echo": content}


@router.get("/search", summary="Search Echo events")
def search_echo(
    query: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    since: Optional[float] = Query(None),
    until: Optional[float] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    cursor: int = Query(0, ge=0),
) -> Dict[str, List[Dict[str, Any]]]:
    """Search logged Echo events stored in Redis."""
    client = get_redis_client()
    if client is None:
        return {"events": [], "next_cursor": None}
    start_ts = since if since is not None else float("-inf")
    end_ts = until if until is not None else float("+inf")

    key: Optional[str] = None
    if level:
        key = f"echo:by_level:{level}"
    elif agent_id:
        key = f"echo:by_agent:{agent_id}"

    if key:
        raw_events = client.zrangebyscore(key, start_ts, end_ts)
    else:
        raw_events = client.lrange("echo:events", 0, -1)

    events = []
    for item in raw_events[cursor : cursor + limit]:
        try:
            data = json.loads(item)
        except json.JSONDecodeError:
            continue
        if agent_id and data.get("agent_id") != agent_id:
            continue
        if level and data.get("level") != level:
            continue
        if query and query not in json.dumps(data):
            continue
        ts = data.get("timestamp", 0)
        if since is not None and ts < since:
            continue
        if until is not None and ts > until:
            continue
        events.append(data)
        if len(events) >= limit:
            break

    next_cursor = (
        cursor + len(events) if len(raw_events) > cursor + len(events) else None
    )
    return {"events": events, "next_cursor": next_cursor}
