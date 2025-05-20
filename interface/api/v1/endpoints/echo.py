import logging
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from interface.api.v1.endpoints.system import _call_orchestrator

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
