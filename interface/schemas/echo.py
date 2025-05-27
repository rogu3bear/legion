from typing import Optional
from pydantic import BaseModel

class EchoLogEntry(BaseModel):
    agent: str
    event: str
    trace_id: str
    timestamp: str
    token_count: Optional[int] = None
    fallback_model: Optional[str] = None
