"""API endpoints for agent management, status, configuration, and lifecycle control."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", summary="List All Agents")
def list_agents() -> List[Dict[str, Any]]:
    """
    Retrieves a list of all registered agents and their current status.
    """
    return [{"name": "test-agent", "status": "active"}]


@router.get("/health", summary="Agent Health Check")
def agent_health() -> Dict[str, str]:
    """Simple health check for agents endpoint."""
    return {"status": "ok"} 