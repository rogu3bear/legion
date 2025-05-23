from __future__ import annotations

"""Payload schema for directive compliance checks."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class DirectivePayload(BaseModel):
    """Information about a directive or request to validate."""

    request_id: Optional[str] = Field(
        None, description="Unique identifier for the request."
    )
    agent_id: Optional[str] = Field(
        None, description="Identifier of the originating agent."
    )
    text: str = Field(..., description="Raw request text to validate.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata such as task or user identifiers.",
    )
    timestamp: Optional[datetime] = Field(
        None, description="Time the directive was produced."
    )

    class Config:
        orm_mode = True
