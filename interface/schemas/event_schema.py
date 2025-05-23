"""Pydantic schema for generic event messages.

TODO: verify field definitions once AGENT_FLOW.md is available.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class Event(BaseModel):
    """Generic event emitted by Legion."""

    type: str = Field(..., description="Event type identifier")
    timestamp: datetime = Field(
        ..., description="UTC timestamp when the event occurred"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict, description="Event-specific data"
    )

    class Config:
        orm_mode = True
