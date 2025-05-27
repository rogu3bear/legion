import logging
import uuid
import json
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from interface.api.v1.endpoints.system import _call_orchestrator
from pydantic import BaseModel
from interface.schemas.echo import EchoLogEntry

logger = logging.getLogger(__name__)
router = APIRouter()


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

@router.get("/logs", response_model=List[EchoLogEntry], summary="Retrieve Echo logs")
def get_echo_logs(agent: str = Query(...), event: Optional[str] = Query(None)) -> List[EchoLogEntry]:
    """Return latest echo logs for a given agent filtered by event."""
    logs_dir = Path("logs/echo")
    entries: List[EchoLogEntry] = []
    if not logs_dir.exists():
        return entries
    for log_file in logs_dir.glob("*.json"):
        try:
            data = json.load(open(log_file))
        except Exception:
            continue
        if data.get("agent") != agent:
            continue
        if event and data.get("event") != event:
            continue
        try:
            entries.append(EchoLogEntry(**data))
        except Exception:
            continue
    entries.sort(key=lambda e: e.timestamp, reverse=True)
    return entries[:100]
