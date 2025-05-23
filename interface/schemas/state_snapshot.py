from __future__ import annotations

"""Snapshot schema of orchestrator state."""

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field

from .agent_status import AgentStatus


class StateSnapshot(BaseModel):
    """Point-in-time view of agents and task queue."""

    timestamp: datetime = Field(..., description="Time the snapshot was generated.")
    agents: Dict[str, AgentStatus] = Field(
        default_factory=dict,
        description="Mapping of agent names to their statuses.",
    )
    tasks_in_queue: List[str] = Field(
        default_factory=list,
        description="Ordered list of queued task IDs.",
    )

    class Config:
        orm_mode = True
