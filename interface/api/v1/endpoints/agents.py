import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

try:
    from interface import dependencies  # type: ignore
    from interface.api.v1.endpoints.system import _call_orchestrator  # type: ignore
    from interface.crud import crud_agent  # type: ignore
    from interface.models.agent import Agent as AgentModel  # type: ignore
    from interface.models.user import User  # type: ignore
    from interface.orchestrator_comm import send_orchestrator_request  # type: ignore
except Exception:  # pragma: no cover - allow partial import failures
    class _Deps:
        def get_db(self) -> Session:
            raise RuntimeError("DB unavailable")

        def get_current_active_user(self) -> Any:
            return None

        def get_current_active_superuser(self) -> Any:
            return None

    dependencies = _Deps()  # type: ignore
    crud_agent = None  # type: ignore
    AgentModel = None  # type: ignore
    User = Any  # type: ignore

    def _call_orchestrator(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {}

    def send_orchestrator_request(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {}
try:
    from interface.schemas.agent import (
        AgentActionResponse,
        AgentConfigInfo,
        AgentConfigUpdate,
        AgentDispatchPayload,
        AgentDispatchResponse,
        AgentStatusInfo,
        AgentRegisterRequest,
        AgentRegisterResponse,
    )
except Exception:  # pragma: no cover - allow partial import failures
    AgentActionResponse = AgentConfigInfo = AgentConfigUpdate = Any  # type: ignore
    AgentDispatchPayload = AgentDispatchResponse = Any  # type: ignore
    AgentStatusInfo = AgentRegisterRequest = AgentRegisterResponse = Any  # type: ignore
try:
    from legion.orchestrator.capability_indexer import get_capabilities  # type: ignore
except Exception:  # pragma: no cover
    def get_capabilities() -> Dict[str, List[str]]:
        return {}


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create Agent")
def create_agent_db(
    agent_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(dependencies.get_current_active_superuser),
    db: Session = Depends(dependencies.get_db),
) -> Dict[str, Any]:
    """Create a new agent in the database (superuser only)."""
    name = agent_data.get("name")
    model = agent_data.get("model")
    if not name or not model:
        raise HTTPException(status_code=400, detail="Missing name or model")
    db_agent = AgentModel(name=name, model=model)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return {"id": db_agent.id, "name": db_agent.name, "model": db_agent.model}


@router.get("/{agent_id}", summary="Get Agent by ID")
def get_agent_db(
    agent_id: int,
    current_user: User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db),
) -> Dict[str, Any]:
    """Retrieve an agent by its ID."""
    db_agent = db.get(AgentModel, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"id": db_agent.id, "name": db_agent.name, "model": db_agent.model}


@router.put("/{agent_id}", summary="Update Agent")
def update_agent_db(
    agent_id: int,
    agent_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(dependencies.get_current_active_superuser),
    db: Session = Depends(dependencies.get_db),
) -> Dict[str, Any]:
    """Update an existing agent (superuser only)."""
    db_agent = db.get(AgentModel, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    new_name = agent_data.get("name")
    if new_name and new_name != db_agent.name:
        existing = (
            db.query(AgentModel)
            .filter(AgentModel.name == new_name, AgentModel.id != agent_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Agent name '{new_name}' already exists.",
            )

    for key, value in agent_data.items():
        if hasattr(db_agent, key):
            setattr(db_agent, key, value)
    db.commit()
    db.refresh(db_agent)
    return {
        "id": db_agent.id,
        "name": db_agent.name,
        "model": db_agent.model,
        "description": db_agent.description,
        "temperature": db_agent.temperature,
        "max_tokens": db_agent.max_tokens,
        "is_active": db_agent.is_active,
        "config": db_agent.config,
        "created_at": db_agent.created_at,
        "last_active": db_agent.last_active,
    }


@router.delete("/{agent_id}", summary="Delete Agent")
def delete_agent_db(
    agent_id: int,
    current_user: User = Depends(dependencies.get_current_active_superuser),
    db: Session = Depends(dependencies.get_db),
) -> Dict[str, Any]:
    """Delete an agent by its ID (superuser only)."""
    db_agent = db.get(AgentModel, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    result = {"id": db_agent.id, "name": db_agent.name, "model": db_agent.model}
    db.delete(db_agent)
    db.commit()
    return result


@router.get("/", response_model=List[AgentStatusInfo], summary="List All Agents")
def list_agents(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> List[AgentStatusInfo]:
    """Retrieve all registered agents and their current status."""
    return crud_agent.get_all_agents_status()


@router.post("/register", summary="Register agent with orchestrator")
def register_agent_legacy(payload: AgentConfigInfo) -> Dict[str, Any]:
    """Forward registration data to the orchestrator."""
    return _call_orchestrator(action="register_agent", payload=payload.dict())


@router.get("/{agent_name}", response_model=AgentStatusInfo, summary="Get Agent Status")
def get_agent_status(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> AgentStatusInfo:
    """Retrieve the detailed status for a specific agent."""
    agent = crud_agent.get_agent_by_name(name=agent_name)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found or failed to retrieve status.",
        )
    return agent


@router.get("/{agent_name}/config", response_model=AgentConfigInfo, summary="Get Agent Configuration")
def get_agent_configuration(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> AgentConfigInfo:
    """Retrieve the current configuration for a specific agent."""
    config = crud_agent.get_agent_config(name=agent_name)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"Config not found for agent '{agent_name}' or failed to retrieve.",
        )
    return AgentConfigInfo(**config)


@router.post("/{agent_name}/dispatch", response_model=AgentDispatchResponse, summary="Dispatch Message to Agent")
def dispatch_message_to_agent(
    agent_name: str,
    payload: AgentDispatchPayload,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> AgentDispatchResponse:
    """Send a message or command to a specific agent via the Orchestrator."""
    logger.info(
        "User '%s' dispatching message to agent '%s'.",
        current_user.username,
        agent_name,
    )

    orchestrator_payload: Dict[str, Any] = {
        "agent_name": agent_name,
        "message": payload.message,
        "context": payload.context or {},
        "originator": {
            "type": "user",
            "id": current_user.id,
            "username": current_user.username,
        },
    }
    if payload.tags is not None:
        orchestrator_payload["tags"] = payload.tags
    if payload.task_owner is not None:
        orchestrator_payload["task_owner"] = payload.task_owner
    if payload.payload is not None:
        orchestrator_payload["payload"] = payload.payload

    response_payload = _call_orchestrator(
        action="dispatch_agent_message", payload=orchestrator_payload
    )

    agent_response = response_payload.get("response")
    received_agent_name = response_payload.get("agent_name", agent_name)
    request_id = response_payload.get("request_id")

    if agent_response is None:
        if response_payload.get("status") == "not_found":
            logger.warning("Agent '%s' not found for dispatch.", agent_name)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found.",
            )
        logger.error(
            "Orchestrator response for dispatch_agent_message ('%s') missing 'response' key.",
            agent_name,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response format from orchestrator for agent dispatch.",
        )

    return AgentDispatchResponse(
        agent_name=received_agent_name,
        response=agent_response,
        request_id=request_id,
    )


@router.post("/{agent_name}/assess", response_model=AgentActionResponse, summary="Trigger Agent Self-Assessment")
def trigger_agent_assessment(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """Trigger a self-assessment process for a specific agent."""
    logger.info(
        "Superuser '%s' triggering assessment for agent '%s'.",
        current_user.username,
        agent_name,
    )

    orchestrator_payload = {"agent_name": agent_name}
    response_payload = _call_orchestrator(action="assess_agent", payload=orchestrator_payload)

    status_report = response_payload.get("status", "unknown")
    message = response_payload.get("message")
    received_agent_name = response_payload.get("agent_name", agent_name)
    request_id = response_payload.get("request_id")

    if status_report == "error" and "not found" in (message or "").lower():
        logger.warning("Agent '%s' not found for assessment trigger.", agent_name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found.",
        )
    if status_report == "error":
        logger.error(
            "Orchestrator failed to trigger assessment for '%s': %s",
            agent_name,
            message,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Orchestrator failed to trigger assessment: {message or 'Unknown error'}",
        )

    return AgentActionResponse(
        agent_name=received_agent_name,
        status=status_report,
        message=message,
        request_id=request_id,
    )


@router.post("/{agent_name}/start", response_model=AgentActionResponse, summary="Start Agent")
def start_agent(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """Send a command to start a specific agent."""
    logger.info(
        "Superuser '%s' requesting start for agent '%s'.",
        current_user.username,
        agent_name,
    )
    response = crud_agent.control_agent_lifecycle(agent_name, "start_agent")
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process request.",
        )
    if response.status == "error":
        if "not found" in (response.detail or "").lower():
            raise HTTPException(status_code=404, detail=response.detail or f"Agent '{agent_name}' not found.")
        raise HTTPException(status_code=502, detail=response.detail or "Orchestrator failed to start agent.")
    return response


@router.post("/{agent_name}/stop", response_model=AgentActionResponse, summary="Stop Agent")
def stop_agent(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """Send a command to stop a specific agent."""
    logger.info(
        "Superuser '%s' requesting stop for agent '%s'.",
        current_user.username,
        agent_name,
    )
    response = crud_agent.control_agent_lifecycle(agent_name, "stop_agent")
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process request.",
        )
    if response.status == "error":
        if "not found" in (response.detail or "").lower():
            raise HTTPException(status_code=404, detail=response.detail or f"Agent '{agent_name}' not found.")
        raise HTTPException(status_code=502, detail=response.detail or "Orchestrator failed to stop agent.")
    return response


@router.post("/{agent_name}/restart", response_model=AgentActionResponse, summary="Restart Agent")
def restart_agent(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """Send a command to restart a specific agent."""
    logger.info(
        "Superuser '%s' requesting restart for agent '%s'.",
        current_user.username,
        agent_name,
    )
    response = crud_agent.control_agent_lifecycle(agent_name, "restart_agent")
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process request.",
        )
    if response.status == "error":
        if "not found" in (response.detail or "").lower():
            raise HTTPException(status_code=404, detail=response.detail or f"Agent '{agent_name}' not found.")
        raise HTTPException(status_code=502, detail=response.detail or "Orchestrator failed to restart agent.")
    return response


@router.put("/{agent_name}/config", response_model=AgentActionResponse, summary="Update Agent Configuration")
def update_agent_configuration(
    agent_name: str,
    config_data: AgentConfigUpdate,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """Update the configuration for a specific agent via the Orchestrator."""
    logger.info(
        "User '%s' updating config for agent '%s'.",
        current_user.username,
        agent_name,
    )

    updated_config = crud_agent.update_agent_config(agent_name=agent_name, config_in=config_data)
    if updated_config is None:
        return AgentActionResponse(
            agent_name=agent_name,
            action="update_config",
            status="error",
            detail=f"Failed to update config for agent '{agent_name}'. Orchestrator did not confirm update or agent not found.",
        )

    return AgentActionResponse(
        agent_name=agent_name,
        action="update_config",
        status="success",
        detail=f"Configuration for agent '{agent_name}' update process initiated.",
        data=updated_config,
    )


@router.post("/reload", response_model=AgentActionResponse, summary="Reload All Agent Configurations")
def reload_all_agents_configs(
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """Trigger a reload of all agent configurations via the Orchestrator."""
    logger.info(
        "Superuser '%s' requesting reload of all agent configurations.",
        current_user.username,
    )
    response = crud_agent.reload_agent_configurations()
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process reload request.",
        )
    if response.status == "error":
        raise HTTPException(status_code=502, detail=response.detail or "Orchestrator failed to reload configurations.")
    return response


@router.get("/capabilities", summary="List Agent Capabilities")
def list_agent_capabilities(
    current_user: User = Depends(dependencies.get_current_active_user),
) -> Dict[str, List[str]]:
    """Return mapping of agents to their capability methods."""
    return get_capabilities()


@router.post("/register", response_model=AgentRegisterResponse, summary="Register Agent")
def register_agent(payload: AgentRegisterRequest) -> AgentRegisterResponse:
    """Register an agent and obtain an auth token."""
    command = {
        "action": "register_agent",
        "payload": payload.model_dump(),
    }
    response = send_orchestrator_request(command)
    if not response or response.get("status") != "success":
        raise HTTPException(status_code=502, detail="Orchestrator registration failed")
    return AgentRegisterResponse(token=response.get("token", ""))
