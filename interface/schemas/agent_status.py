from __future__ import annotations

"""Runtime status representation for an agent."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentStatus(BaseModel):
    """Lightweight status snapshot for an agent."""

    name: str = Field(..., description="Unique agent name.")
    status: str = Field(..., description="Current operational status.")
    is_active: bool = Field(..., description="Whether the agent is active.")
    last_heartbeat: Optional[datetime] = Field(
        None, description="Timestamp of the last heartbeat."
    )
    capabilities: List[str] = Field(
        default_factory=list, description="Capabilities supported by the agent."
    )
    tasks: Optional[int] = Field(
        None, description="Number of tasks currently assigned."
    )

    class Config:
        orm_mode = True
