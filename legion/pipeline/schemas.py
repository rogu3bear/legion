from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class InternalRequest:
    """Internal representation of a Discord command request."""

    user_id: str
    command: str
    args: Dict[str, Any]
    channel: str
    agent_key: str


@dataclass
class AgentResponse:
    """Standard response object returned by agents."""

    text: str
