"""Main FastAPI entrypoint for Legion Middleware Service"""

import asyncio
from types import SimpleNamespace

import prometheus_client
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from .config import settings
from .middleware.chroma_client import ChromaClient
from .middleware.context_manager import ContextManager
from .middleware.hallucination_guard import HallucinationGuard
from .models import ChromaRecord, OrchestratorRequest, OrchestratorResponse

app = FastAPI(title="Legion Middleware Service", version="0.1.0")


# Health endpoint
@app.get("/health", response_class=JSONResponse)
async def health():
    return {"status": "ok"}


# Metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return prometheus_client.generate_latest()


# Authentication dependency stub
async def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if not token or token != f"Bearer {settings.API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


# Route to orchestrator
@app.post("/orchestrate", dependencies=[Depends(verify_token)])
async def orchestrate(payload: dict):
    # TODO: attach core directives, forward to orchestrator, handle response
    return {"message": "stub"}


# Initialize context manager
ctx_mgr = ContextManager(None)
# Initialize Chroma client and hallucination guard
try:
    tmp_chroma = ChromaClient(settings.CHROMA_API_URL, settings.CHROMA_API_KEY)
    # Fallback if client does not support get_collection
    if not hasattr(tmp_chroma.client, "get_collection"):
        raise ValueError("Chroma client unavailable")
    chroma = tmp_chroma
except Exception:
    # Fallback dummy client for testing or when Chroma server is unavailable
    dummy_client = SimpleNamespace(
        get_collection=lambda name: SimpleNamespace(get=lambda ids: None)
    )
    chroma = SimpleNamespace(client=dummy_client)
guard = HallucinationGuard()


# Insert middleware into request lifecycle
@app.middleware("http")
async def attach_context(request: Request, call_next):
    # TODO: extract agent info, attach context, log to central state
    response = await call_next(request)
    return response


@app.post(
    "/invoke", dependencies=[Depends(verify_token)], response_model=OrchestratorResponse
)
async def invoke(req: OrchestratorRequest):
    raw = await ctx_mgr.route(req.data)
    try:
        await chroma.upsert_embedding(ChromaRecord(**req.data))
        await chroma.upsert_embedding(ChromaRecord(**raw))
    except Exception:
        pass
    guard.filter(raw)
    return OrchestratorResponse(data=raw)


@app.get("/context/{agent_name}/{interaction_id}")
async def get_context(agent_name: str, interaction_id: str):
    # Support both async and sync get_collection
    maybe_coll = chroma.client.get_collection(agent_name)
    if asyncio.iscoroutine(maybe_coll):
        coll = await maybe_coll
    else:
        coll = maybe_coll
    return await coll.get(ids=[f"{agent_name}:{interaction_id}"])
