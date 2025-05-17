"""Pydantic models for middleware"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ChromaRecord(BaseModel):
    agent_name: str
    interaction_id: str
    role: str
    tokens: int
    embedding: List[float]
    timestamp: datetime
    tags: List[str] = Field(default_factory=list)


class OrchestratorRequest(BaseModel):
    # TODO: define request schema
    data: dict


class OrchestratorResponse(BaseModel):
    # TODO: define response schema
    data: dict
