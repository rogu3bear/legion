from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class MCPContext:
    """Context object for MCP operations."""

    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
