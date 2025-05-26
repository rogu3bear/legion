from fastapi import APIRouter, HTTPException

from legion.state_repo import repo as state_repo

router = APIRouter()


@router.post("/agent/register")
def register_agent(payload: dict):
    """Register an agent and return a token."""
    agent_id = payload.get("id")
    role = payload.get("role")
    caps = payload.get("caps", [])
    if not agent_id or not role:
        raise HTTPException(status_code=400, detail="Missing id or role")
    token = state_repo.register_agent(agent_id, role, caps)
    return {"token": token}


@router.get("/agent/{agent_id}/status")
def agent_status(agent_id: str):
    status = state_repo.get_agent_status(agent_id)
    if status is None:
        raise HTTPException(status_code=404, detail="agent not found")
    return status
