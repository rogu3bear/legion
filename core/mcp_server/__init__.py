"""
MCP Server module for Legion.
"""

# Re-export the main server components
try:
    from ..mcp_server import LegionMCPServer, get_mcp_server

    __all__ = ["LegionMCPServer", "get_mcp_server"]
except ImportError:
    # Fallback if direct import doesn't work
    __all__ = []
