from fastapi import APIRouter, Path

from legion.task_queue import queue
from legion.orchestrator.state_repo import repo as state_repo

router = APIRouter()


@router.get("/queue/summary")
def get_queue_summary() -> dict:
    """Return counts of tasks grouped by priority/state."""
    return queue.summary()


@router.get("/agent/{agent_id}/tasks")
def get_agent_tasks(agent_id: str = Path(...)) -> list:
    """List current and recent tasks for an agent."""
    return state_repo.get_agent_tasks(agent_id)
