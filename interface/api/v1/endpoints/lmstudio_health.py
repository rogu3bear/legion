"""Health check endpoint for LM Studio MCP Bridge."""

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/lmstudio/health", summary="Check LM Studio MCP Bridge health")
async def lmstudio_health() -> JSONResponse:
    """
    Check the health of the LM Studio MCP bridge and underlying LM Studio service.

    Returns:
        JSONResponse: Health status including MCP bridge and LM Studio server status
    """
    health_status = {
        "mcp_bridge": {"status": "unknown"},
        "lmstudio_server": {"status": "unknown"},
        "overall": {"status": "unknown"}
    }

    try:
        # Check if LM Studio MCP bridge is running
        mcp_port = int(os.getenv("LMSTUDIO_MCP_PORT", "8009"))

        async with httpx.AsyncClient() as client:
            try:
                # Check MCP bridge health endpoint
                mcp_response = await client.get(
                    f"http://localhost:{mcp_port}/health",
                    timeout=5.0
                )

                if mcp_response.status_code == 200:
                    mcp_data = mcp_response.json()
                    health_status["mcp_bridge"] = {
                        "status": "healthy",
                        "port": mcp_port,
                        "response": mcp_data
                    }

                    # If MCP bridge is healthy, it should have info about LM Studio
                    if "status" in mcp_data:
                        health_status["lmstudio_server"] = {
                            "status": mcp_data.get("status", "unknown"),
                            "base_url": mcp_data.get("base_url"),
                            "models_available": mcp_data.get("models_available", 0)
                        }
                else:
                    health_status["mcp_bridge"] = {
                        "status": "unhealthy",
                        "port": mcp_port,
                        "error": f"HTTP {mcp_response.status_code}"
                    }

            except httpx.ConnectError:
                health_status["mcp_bridge"] = {
                    "status": "unreachable",
                    "port": mcp_port,
                    "error": "Connection refused - MCP bridge not running"
                }
            except httpx.TimeoutException:
                health_status["mcp_bridge"] = {
                    "status": "timeout",
                    "port": mcp_port,
                    "error": "Health check timed out"
                }

    except Exception as e:
        logger.error(f"Error checking LM Studio MCP health: {e}")
        health_status["mcp_bridge"] = {
            "status": "error",
            "error": str(e)
        }

    # If MCP bridge status is unknown, try direct LM Studio check
    if health_status["lmstudio_server"]["status"] == "unknown":
        try:
            lmstudio_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{lmstudio_url}/models", timeout=5.0)

                if response.status_code == 200:
                    models_data = response.json()
                    health_status["lmstudio_server"] = {
                        "status": "healthy",
                        "base_url": lmstudio_url,
                        "models_available": len(models_data.get("data", []))
                    }
                else:
                    health_status["lmstudio_server"] = {
                        "status": "unhealthy",
                        "base_url": lmstudio_url,
                        "error": f"HTTP {response.status_code}"
                    }

        except httpx.ConnectError:
            health_status["lmstudio_server"] = {
                "status": "unreachable",
                "error": "LM Studio server not running"
            }
        except Exception as e:
            health_status["lmstudio_server"] = {
                "status": "error",
                "error": str(e)
            }

    # Determine overall status
    mcp_healthy = health_status["mcp_bridge"]["status"] == "healthy"
    lmstudio_healthy = health_status["lmstudio_server"]["status"] == "healthy"

    if mcp_healthy and lmstudio_healthy:
        health_status["overall"]["status"] = "healthy"
        status_code = 200
    elif mcp_healthy or lmstudio_healthy:
        health_status["overall"]["status"] = "degraded"
        status_code = 200
    else:
        health_status["overall"]["status"] = "unhealthy"
        status_code = 503

    # Add configuration info
    health_status["configuration"] = {
        "llm_mode": os.getenv("LLM_MODE", "not_set"),
        "mcp_port": int(os.getenv("LMSTUDIO_MCP_PORT", "8009")),
        "lmstudio_base_url": os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
        "model": os.getenv("OPENAI_MODEL", "meta-llama-3.1-8b-instruct")
    }

    return JSONResponse(content=health_status, status_code=status_code)


@router.get("/lmstudio/models", summary="List available models in LM Studio")
async def lmstudio_models() -> JSONResponse:
    """
    Get the list of available models from LM Studio.

    Returns:
        JSONResponse: List of available models
    """
    try:
        lmstudio_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{lmstudio_url}/models", timeout=10.0)
            response.raise_for_status()

            return JSONResponse(content=response.json())

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="LM Studio server is not reachable"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request to LM Studio timed out"
        )
    except Exception as e:
        logger.error(f"Error fetching LM Studio models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch models: {e!s}"
        )
