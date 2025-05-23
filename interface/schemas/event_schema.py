from __future__ import annotations

"""Schema definitions for system events."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class Event(BaseModel):
    """Generic event emitted by Legion components."""

    type: str = Field(..., description="Event type identifier.")
    timestamp: datetime = Field(
        ..., description="Time the event occurred (UTC)."
    )
    data: Dict[str, Any] = Field(
        default_factory=dict, description="Event-specific payload data."
    )

    class Config:
        orm_mode = True
