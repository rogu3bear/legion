"""API endpoints for proxying requests to LM Studio."""

import asyncio
import logging
import os
import time
from collections import defaultdict, deque

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from interface.api.v1.schemas import ChatRequest
from interface.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple in-memory rate limiter (10 requests per minute per IP)
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 60  # seconds
request_tracker = defaultdict(deque)

# HTTP client configuration
TIMEOUT = httpx.Timeout(60.0, connect=10.0)
RETRIES = 2

# Determine LM Studio base URL from environment or default
# The .env.ports.example uses LMSTUDIO_API_URL=http://127.0.0.1:1234/v1
# We need to ensure the /v1 is handled correctly, as the variable itself contains it.
# For a completions endpoint, it's typically /v1/chat/completions or /v1/completions.

LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_API_URL", "http://127.0.0.1:1234/v1")
# Ensure LMSTUDIO_BASE_URL ends with /v1 if not already
if not LMSTUDIO_BASE_URL.endswith("/v1"):
    if LMSTUDIO_BASE_URL.endswith("/"):
        LMSTUDIO_BASE_URL += "v1"
    else:
        LMSTUDIO_BASE_URL += "/v1"

# Define the specific completion path
LMSTUDIO_COMPLETION_ENDPOINT = f"{LMSTUDIO_BASE_URL}/chat/completions"


def redact_messages_for_logging(payload: dict) -> dict:
    """Redact message content from payload for privacy-safe logging."""
    if not settings.DEBUG and "messages" in payload:
        redacted_payload = payload.copy()
        redacted_payload["messages"] = [
            {**msg, "content": "[REDACTED]"} for msg in payload["messages"]
        ]
        return redacted_payload
    return payload


def check_rate_limit(client_ip: str) -> bool:
    """Check if client IP is within rate limits. Returns True if allowed."""
    now = time.time()

    # Clean old requests outside the window
    while request_tracker[client_ip] and request_tracker[client_ip][0] <= now - RATE_LIMIT_WINDOW:
        request_tracker[client_ip].popleft()

    # Check if within limit
    if len(request_tracker[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False

    # For non-streaming requests, add immediately
    # For streaming, we'll add in finally block after completion
    return True


def register_rate_limit_hit(client_ip: str):
    """Register a completed request for rate limiting."""
    request_tracker[client_ip].append(time.time())


@router.post("/echo", summary="Proxy payload to LM Studio completion endpoint")
async def lmstudio_echo(request: Request) -> JSONResponse:
    """
    Receives a JSON payload and proxies it directly to the configured LM Studio
    chat completions endpoint (e.g., `/v1/chat/completions`).
    Returns the raw JSON response from LM Studio.
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload received for /lmstudio/echo: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from e

    logger.debug(
        f"Proxying payload to LM Studio endpoint: {LMSTUDIO_COMPLETION_ENDPOINT}"
    )
    logger.debug(f"Payload: {redact_messages_for_logging(payload)}")

    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        try:
            for attempt in range(RETRIES + 1):
                try:
                    response = await client.post(
                        LMSTUDIO_COMPLETION_ENDPOINT,
                        json=payload,
                        headers=request.headers.raw,  # Forward original headers if necessary, be cautious with sensitive ones
                    )
                    response.raise_for_status()  # Raise an exception for HTTP 4xx or 5xx errors

                    # Return the raw JSON response from LM Studio
                    return JSONResponse(
                        content=response.json(), status_code=response.status_code
                    )
                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    if attempt == RETRIES:
                        raise
                    logger.warning(f"Retry {attempt + 1}/{RETRIES} after error: {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff

        except httpx.ConnectError as e:
            logger.error(
                f"Could not connect to LM Studio at {LMSTUDIO_COMPLETION_ENDPOINT}: {e}"
            )
            raise HTTPException(
                status_code=503, detail=f"Could not connect to LM Studio: {e}"
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Request to LM Studio timed out: {e}")
            raise HTTPException(
                status_code=504, detail=f"Request to LM Studio timed out: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(
                f"LM Studio returned an error: {e.response.status_code} - {e.response.text}"
            )
            # Forward the error response from LM Studio if possible
            return JSONResponse(
                content=e.response.json()
                if e.response.content
                else {"detail": e.response.text},
                status_code=e.response.status_code,
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while proxying to LM Studio: {e}"
            )
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {e}"
            ) from e


@router.post("/chat", summary="Structured chat endpoint for LM Studio")
async def lmstudio_chat(chat_request: ChatRequest, request: Request):
    """
    Structured chat endpoint that formats messages for LM Studio compatibility.
    Accepts structured chat messages and forwards them to LM Studio.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit first
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too Many Requests",
                "message": f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds.",
                "retry_after": RATE_LIMIT_WINDOW
            }
        )

    # Patch: Ensure sensible defaults and pass-through for model/stream/temperature
    payload = {
        "messages": [{"role": msg.role, "content": msg.content} for msg in chat_request.messages],
        "temperature": chat_request.temperature,
        "max_tokens": chat_request.max_tokens if chat_request.max_tokens and chat_request.max_tokens > 0 else 256,
        "stream": chat_request.stream,
    }

    # Pass through model if present in request body
    try:
        body = await request.json()
        if "model" in body:
            payload["model"] = body["model"]
    except Exception:
        pass

    logger.debug(f"Sending structured chat request to LM Studio: {redact_messages_for_logging(payload)}")

    request_completed = False
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            try:
                if payload.get("stream"):
                    # Streaming mode
                    for attempt in range(RETRIES + 1):
                        try:
                            upstream_response = await client.post(
                                LMSTUDIO_COMPLETION_ENDPOINT,
                                json=payload,
                                stream=True,
                            )
                            upstream_response.raise_for_status()
                            request_completed = True
                            return StreamingResponse(upstream_response.aiter_bytes(), media_type="application/x-ndjson")
                        except (httpx.ConnectError, httpx.TimeoutException) as e:
                            if attempt == RETRIES:
                                raise
                            logger.warning(f"Streaming retry {attempt + 1}/{RETRIES} after error: {e}")
                            await asyncio.sleep(0.5 * (attempt + 1))
                else:
                    # Non-streaming mode
                    for attempt in range(RETRIES + 1):
                        try:
                            response = await client.post(
                                LMSTUDIO_COMPLETION_ENDPOINT,
                                json=payload,
                            )
                            response.raise_for_status()
                            request_completed = True
                            return JSONResponse(
                                content=response.json(), status_code=response.status_code
                            )
                        except (httpx.ConnectError, httpx.TimeoutException) as e:
                            if attempt == RETRIES:
                                raise
                            logger.warning(f"Non-streaming retry {attempt + 1}/{RETRIES} after error: {e}")
                            await asyncio.sleep(0.5 * (attempt + 1))

            except httpx.ConnectError as e:
                logger.error(f"Could not connect to LM Studio: {e}")
                raise HTTPException(
                    status_code=503, detail=f"LM Studio connection failed: {e}"
                ) from e
            except httpx.TimeoutException as e:
                logger.error(f"LM Studio request timed out: {e}")
                raise HTTPException(
                    status_code=504, detail=f"LM Studio timeout: {e}"
                ) from e
            except httpx.HTTPStatusError as e:
                logger.error(f"LM Studio error: {e.response.status_code}")
                request_completed = True  # Count HTTP errors as completed requests
                return JSONResponse(
                    content=e.response.json() if e.response.content else {"detail": e.response.text},
                    status_code=e.response.status_code,
                )
            except Exception as e:
                logger.error(f"Unexpected error in chat endpoint: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Chat request failed: {e}"
                ) from e
    finally:
        # Register rate limit hit only after request completion
        if request_completed or not payload.get("stream"):
            register_rate_limit_hit(client_ip)
