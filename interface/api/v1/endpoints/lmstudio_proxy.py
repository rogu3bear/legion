"""API endpoints for proxying requests to LM Studio."""

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()

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
    logger.debug(f"Payload: {payload}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                LMSTUDIO_COMPLETION_ENDPOINT,
                json=payload,
                headers=request.headers.raw,  # Forward original headers if necessary, be cautious with sensitive ones
                timeout=60.0,  # Set a reasonable timeout
            )
            response.raise_for_status()  # Raise an exception for HTTP 4xx or 5xx errors

            # Return the raw JSON response from LM Studio
            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )

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
                content=e.response.json() if e.response.content else {"detail": e.response.text},
                status_code=e.response.status_code,
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while proxying to LM Studio: {e}"
            )
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {e}"
            ) from e
