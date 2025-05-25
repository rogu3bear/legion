"""LM Studio MCP Bridge for Legion."""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from core.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


class LMStudioAdapter:
    """Adapter for LM Studio REST API calls."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the LM Studio adapter."""
        self.base_url = base_url or os.getenv("LMSTUDIO_API_URL", "http://127.0.0.1:1234/v1")
        if not self.base_url.endswith("/v1"):
            self.base_url = self.base_url.rstrip("/") + "/v1"
        
        self.completions_endpoint = f"{self.base_url}/chat/completions"
        self.models_endpoint = f"{self.base_url}/models"
        
        logger.info(f"LMStudioAdapter initialized with base_url: {self.base_url}")

    async def discover_model(self) -> Dict[str, Any]:
        """Discover available models from LM Studio."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.models_endpoint, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to discover models: {e}")
                return {"error": str(e), "models": []}

    async def chat_complete(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request to LM Studio."""
        payload = {
            "model": kwargs.get("model", os.getenv("OPENAI_MODEL", "meta-llama-3.1-8b-instruct")),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k not in ("model", "messages", "max_tokens", "temperature")}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.completions_endpoint,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Chat completion failed: {e}")
                raise HTTPException(status_code=503, detail=f"LM Studio request failed: {e}")

    async def raw_generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send raw generation request to LM Studio."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.completions_endpoint,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Raw generation failed: {e}")
                raise HTTPException(status_code=503, detail=f"LM Studio request failed: {e}")

    async def stats(self) -> Dict[str, Any]:
        """Get LM Studio health and statistics."""
        try:
            models = await self.discover_model()
            return {
                "status": "healthy",
                "base_url": self.base_url,
                "models_available": len(models.get("data", [])),
                "models": models
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "base_url": self.base_url,
                "error": str(e)
            }


class LMStudioMCP:
    """LM Studio MCP Server."""

    def __init__(self, adapter: Optional[LMStudioAdapter] = None):
        """Initialize the MCP server."""
        self.adapter = adapter or LMStudioAdapter()
        self.app = FastAPI(title="LM Studio MCP Bridge", version="1.0.0")
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes for the MCP server."""
        
        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: Request):
            """Handle chat completions requests."""
            try:
                payload = await request.json()
                messages = payload.get("messages", [])
                result = await self.adapter.chat_complete(messages, **payload)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Chat completions endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/v1/generate")
        async def generate(request: Request):
            """Handle raw generation requests."""
            try:
                payload = await request.json()
                result = await self.adapter.raw_generate(payload)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Generate endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            stats = await self.adapter.stats()
            status_code = 200 if stats.get("status") == "healthy" else 503
            return JSONResponse(content=stats, status_code=status_code)

        @self.app.get("/models")
        async def models():
            """List available models."""
            try:
                result = await self.adapter.discover_model()
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Models endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))


# Factory function for DI container
def create_lmstudio_adapter() -> LMStudioAdapter:
    """Factory function to create LM Studio adapter."""
    return LMStudioAdapter()


def create_lmstudio_mcp() -> LMStudioMCP:
    """Factory function to create LM Studio MCP server."""
    return LMStudioMCP() 