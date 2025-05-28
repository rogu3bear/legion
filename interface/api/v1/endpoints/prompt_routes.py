import asyncio
import hashlib
import logging
import os
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from interface.api.v1.endpoints.system import _call_orchestrator
from legion.middleware.context_resolver import resolve_prompt
from legion.middleware.retry_handler import retry_prompt
from legion.middleware.therapist_bridge import RetryTrigger, should_retry_from_therapist

logger = logging.getLogger(__name__)
router = APIRouter()


class PromptPayload(BaseModel):
    agent_name: str
    prompt: str


@router.post("/prompt", summary="Process prompt with retry and fallback")
async def process_prompt(payload: PromptPayload) -> Dict[str, Any]:
    ctx = await resolve_prompt(payload.prompt, f"context:{payload.agent_name}")
    use_lmstudio = ctx["use_lmstudio"]
    trace_id = hashlib.sha256(os.urandom(16)).hexdigest()

    async def _call() -> Dict[str, Any]:
        orch_payload = {
            "agent_name": payload.agent_name,
            "message": payload.prompt,
            "context": ctx["context"] or {},
            "use_lmstudio": use_lmstudio,
        }
        response = await asyncio.to_thread(
            _call_orchestrator, "dispatch_agent_message", orch_payload
        )
        if should_retry_from_therapist(response):
            raise RetryTrigger("therapist signaled retry")
        return response

    try:
        return await retry_prompt(_call)
    except RetryTrigger:
        raise HTTPException(status_code=503, detail="Therapist requested retry")
    except Exception as exc:  # noqa: BLE001
        logger.error("Prompt processing failed", exc_info=exc)
        raise HTTPException(status_code=500, detail=str(exc))
