from __future__ import annotations

import os
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException

from interface.orchestrator_comm import send_request

router = APIRouter()


@router.get("/agents/diagnostics")
def get_agents_diagnostics(
    check: bool = False,
    x_internal_key: str | None = Header(default=None, alias="X-Internal-Key"),
) -> Dict[str, Any]:
    expected = os.getenv("INTERNAL_API_KEY")
    if not expected or x_internal_key != expected:
        raise HTTPException(status_code=403, detail="Forbidden")

    command = {
        "action": "agents_diagnostics",
        "payload": {"check": check},
        "request_id": str(uuid.uuid4()),
    }
    response = send_request(command)
    if response is None:
        raise HTTPException(status_code=503, detail="No response from orchestrator")
    return response.get("response", {})
