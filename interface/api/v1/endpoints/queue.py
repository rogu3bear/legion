from typing import Dict, Any, Optional
from fastapi import APIRouter, Path, Query, Depends, HTTPException

from legion.task_queue import queue
from legion.orchestrator import state_repo
from interface import dependencies
from interface.models.user import User

router = APIRouter()


@router.get("/queue/summary")
def get_queue_summary() -> dict:
    """Return counts of tasks grouped by priority/state."""
    return queue.summary()


@router.get("/queue/agents/{agent_name}/stats")
def get_agent_queue_stats(
    agent_name: str = Path(..., description="Name of the agent"),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Dict[str, Any]:
    """Get detailed queue statistics for a specific agent."""
    stats = queue.get_agent_queue_stats(agent_name)
    stats["agent"] = agent_name
    stats["queue_length"] = queue.get_agent_queue_length(agent_name)
    return stats


@router.get("/queue/agents/{agent_name}/length")
def get_agent_queue_length(
    agent_name: str = Path(..., description="Name of the agent"),
) -> Dict[str, Any]:
    """Get the number of queued tasks for a specific agent."""
    length = queue.get_agent_queue_length(agent_name)
    return {
        "agent": agent_name,
        "queue_length": length,
    }


@router.post("/queue/cleanup")
def cleanup_completed_tasks(
    max_age_hours: Optional[int] = Query(24, description="Maximum age in hours for completed tasks to keep"),
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Dict[str, Any]:
    """Clean up old completed/failed tasks to prevent memory bloat."""
    if max_age_hours < 1 or max_age_hours > 168:  # 1 hour to 1 week
        raise HTTPException(status_code=400, detail="max_age_hours must be between 1 and 168")
    
    cleaned_count = queue.cleanup_completed_tasks(max_age_hours)
    return {
        "cleaned_tasks": cleaned_count,
        "max_age_hours": max_age_hours,
        "message": f"Cleaned up {cleaned_count} old completed/failed tasks",
    }


@router.get("/queue/health")
def get_queue_health() -> Dict[str, Any]:
    """Get queue health and performance metrics."""
    try:
        summary = queue.summary()
        total_tasks = sum(summary.values())
        
        # Calculate basic health metrics
        queued_ratio = summary.get("queued", 0) / max(total_tasks, 1)
        failed_ratio = summary.get("failed", 0) / max(total_tasks, 1)
        
        health_status = "healthy"
        if failed_ratio > 0.1:  # More than 10% failed
            health_status = "degraded"
        elif queued_ratio > 0.8:  # More than 80% queued (potential backlog)
            health_status = "backlogged"
        
        return {
            "status": health_status,
            "total_tasks": total_tasks,
            "task_breakdown": summary,
            "metrics": {
                "queued_ratio": round(queued_ratio, 3),
                "failed_ratio": round(failed_ratio, 3),
            },
            "redis_connected": queue.client is not None,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "redis_connected": False,
        }
