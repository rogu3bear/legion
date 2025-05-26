"""MCP Bridges for Legion."""

from .lmstudio_bridge import (
    LMStudioAdapter,
    LMStudioMCP,
    create_lmstudio_adapter,
    create_lmstudio_mcp,
)

__all__ = [
    "LMStudioAdapter",
    "LMStudioMCP",
    "create_lmstudio_adapter",
    "create_lmstudio_mcp",
]
