"""Schema describing directive payload structure.

TODO: verify field definitions once AGENT_FLOW.md is available.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class DirectivePayload(BaseModel):
    """Instruction data sent to the orchestrator."""

    agent: str = Field(..., description="Target agent identifier")
    directive: str = Field(..., description="Directive name requested")
    params: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Optional directive parameters"
    )

    class Config:
        orm_mode = True
