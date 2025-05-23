"""Model for capturing orchestrator state snapshots.

TODO: verify fields when AGENT_FLOW.md is restored.
"""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .agent_status import AgentStatus
from .task import Task


class StateSnapshot(BaseModel):
    """Snapshot of the system state."""

    timestamp: datetime = Field(..., description="Timestamp of the snapshot")
    agents: List[AgentStatus] = Field(
        default_factory=list, description="Current agent statuses"
    )
    tasks: List[Task] = Field(
        default_factory=list, description="List of active or queued tasks"
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict, description="System metrics at this time"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Configuration settings"
    )

    class Config:
        orm_mode = True
