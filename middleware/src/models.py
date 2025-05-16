"""Pydantic models for middleware"""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class ChromaRecord(BaseModel):
    agent_name: str
    interaction_id: str
    role: str
    tokens: int
    embedding: List[float]
    timestamp: datetime
    tags: List[str] = []


class OrchestratorRequest(BaseModel):
    # TODO: define request schema
    data: dict


class OrchestratorResponse(BaseModel):
    # TODO: define response schema
    data: dict
