"""Simplified agent status schema.

TODO: update fields if AGENT_FLOW.md provides a different structure.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentStatus(BaseModel):
    """Current runtime status information for an agent."""

    name: str = Field(..., description="Agent unique name")
    status: str = Field(..., description="Current status of the agent")
    uptime: Optional[float] = Field(
        None, description="Seconds the agent has been running"
    )
    messages_processed: Optional[int] = Field(
        None, description="Total number of processed messages"
    )
    last_message: Optional[str] = Field(
        None, description="Content of the last processed message"
    )
    last_message_time: Optional[datetime] = Field(
        None, description="Timestamp of last processed message"
    )
    error_count: Optional[int] = Field(
        None, description="Total number of errors encountered"
    )
    last_error: Optional[str] = Field(
        None, description="Most recent error message if any"
    )
    last_error_time: Optional[datetime] = Field(
        None, description="Timestamp of the last error"
    )

    class Config:
        orm_mode = True
