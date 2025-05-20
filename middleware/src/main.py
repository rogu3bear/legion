"""Main FastAPI entrypoint for Legion Middleware Service"""

import asyncio
import logging
import uuid
from datetime import datetime
from types import SimpleNamespace

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

import prometheus_client
from legion.core.utils.chroma_client import AsyncChromaClient as ChromaClient

from .config import settings
from .middleware.context_manager import ContextManager
from .middleware.hallucination_guard import HallucinationGuard
from .models import ChromaRecord, OrchestratorRequest, OrchestratorResponse

app = FastAPI(title="Legion Middleware Service", version="0.1.0")
logger = logging.getLogger(__name__)

# Counter for request metrics
REQUEST_COUNTER = prometheus_client.Counter(
    "middleware_requests_total",
    "Total count of requests processed by the middleware",
    ["endpoint", "status"],
)


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
    """
    Process orchestration requests by adding directives and forwarding to the orchestrator.

    Args:
        payload: The request payload to forward to the orchestrator.

    Returns:
        The orchestrator's response.
    """
    # Track the request
    REQUEST_COUNTER.labels(endpoint="orchestrate", status="received").inc()

    try:
        # Add request tracking
        if "request_id" not in payload:
            payload["request_id"] = str(uuid.uuid4())

        # Add timestamp
        if "timestamp" not in payload:
            payload["timestamp"] = datetime.utcnow().isoformat()

        # Attach core directives via context manager
        enriched_payload = await ctx_mgr.attach_core_directives(payload)

        # Forward to orchestrator
        if ctx_mgr.client:
            # This is the real implementation when the client is available
            response = await ctx_mgr.client.send(enriched_payload)
        else:
            # Stub response when no client is available
            response = {
                "status": "success",
                "message": "Request processed by orchestrator (stub)",
                "request_id": payload.get("request_id"),
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Log the interaction
        await ctx_mgr.log_interaction({**enriched_payload, "response": response})

        # Track successful request
        REQUEST_COUNTER.labels(endpoint="orchestrate", status="success").inc()

        return response

    except Exception as e:
        # Track failed request
        REQUEST_COUNTER.labels(endpoint="orchestrate", status="error").inc()
        logger.exception(f"Error in orchestrate endpoint: {e}")
        # Return error response
        return {
            "status": "error",
            "message": f"Error processing request: {e!s}",
            "request_id": payload.get("request_id"),
            "timestamp": datetime.utcnow().isoformat(),
        }


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
    """
    HTTP middleware to extract agent info, attach context, and log to central state.

    Args:
        request: The incoming HTTP request.
        call_next: Function to call the next middleware or route handler.

    Returns:
        The HTTP response.
    """
    # Generate a request ID
    request_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    # Add request ID to the request state so it's accessible in route handlers
    request.state.request_id = request_id

    # Extract user info from headers or token
    user_id = "anonymous"
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # In a real implementation, this would decode and validate the token
        # For now, just use a placeholder user ID
        user_id = "authenticated_user"

    # Extract agent info from path
    path = request.url.path
    agent_name = "unknown"
    if "/agents/" in path:
        parts = path.split("/")
        for i, part in enumerate(parts):
            if part == "agents" and i + 1 < len(parts):
                agent_name = parts[i + 1]
                break

    # Create context data
    context_data = {
        "request_id": request_id,
        "user_id": user_id,
        "agent": agent_name,
        "path": path,
        "method": request.method,
        "timestamp": start_time.isoformat(),
    }

    # Log the start of the request
    logger.info(
        f"Request started: {request.method} {path}",
        extra={"request_id": request_id, "user_id": user_id},
    )

    # Add context data to request state for use in route handlers
    request.state.context = context_data

    try:
        # Process the request
        response = await call_next(request)

        # Calculate request duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        # Add response info to context
        context_data["status_code"] = response.status_code
        context_data["duration"] = duration

        # Log the interaction
        await ctx_mgr.log_interaction(context_data)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Log the completion of the request
        logger.info(
            f"Request completed: {request.method} {path} {response.status_code} in {duration:.3f}s",
            extra={"request_id": request_id, "status_code": response.status_code},
        )

        return response

    except Exception as e:
        # Log the error
        logger.exception(
            f"Error processing request: {request.method} {path} - {e!s}",
            extra={"request_id": request_id},
        )

        # Add error info to context
        context_data["error"] = str(e)
        context_data["status_code"] = 500

        # Log the interaction with error
        await ctx_mgr.log_interaction(context_data)

        # Return error response
        error_response = JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Internal server error: {e!s}",
                "request_id": request_id,
            },
        )
        error_response.headers["X-Request-ID"] = request_id

        return error_response


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
