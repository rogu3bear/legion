"""API endpoints for agent management, status, configuration, and lifecycle control."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from interface import dependencies
from interface.api.v1.endpoints.system import _call_orchestrator  # Import helper
from interface.crud import crud_agent
from interface.models.agent import Agent as AgentModel
from interface.models.user import User
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
from interface.orchestrator_comm import send_orchestrator_request
from legion.orchestrator.capability_indexer import get_capabilities

logger = logging.getLogger(__name__)
router = APIRouter()


# --- DB CRUD Endpoints for Agent Model (moved up) ---
@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create Agent")
def create_agent_db(
    agent_data: dict = Body(...),
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
    agent_data: dict = Body(...),
    current_user: User = Depends(dependencies.get_current_active_superuser),
    db: Session = Depends(dependencies.get_db),
) -> Dict[str, Any]:
    """Update an existing agent (superuser only)."""
    db_agent = db.get(AgentModel, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # If name is being updated, check for conflicts first
    new_name = agent_data.get("name")
    if new_name and new_name != db_agent.name:
        existing_agent_with_name = (
            db.query(AgentModel)
            .filter(AgentModel.name == new_name, AgentModel.id != agent_id)
            .first()
        )
        if existing_agent_with_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Agent name '{new_name}' already exists.",
            )

    # Apply updates for provided fields
    for key, value in agent_data.items():
        if hasattr(db_agent, key):
            setattr(db_agent, key, value)
    db.commit()
    db.refresh(db_agent)
    # Return all relevant fields from the model after update
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
    """
    Retrieves a list of all registered agents and their current status.

    Communicates with the Orchestrator to get the latest information.
    Requires an active user session.
    """
    agents = crud_agent.get_all_agents_status()  # Changed from get_agents()
    return agents


@router.get("/{agent_name}", response_model=AgentStatusInfo, summary="Get Agent Status")
def get_agent_status(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> AgentStatusInfo:
    """
    Retrieves the detailed status for a specific agent.

    - **agent_name**: The name of the agent to query.

    Communicates with the Orchestrator.
    Requires an active user session.
    Raises HTTP 404 if the agent is not found.
    """
    agent = crud_agent.get_agent_by_name(name=agent_name)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found or failed to retrieve status.",
        )
    return agent


@router.get(
    "/{agent_name}/config",
    response_model=AgentConfigInfo,
    summary="Get Agent Configuration",
)
def get_agent_configuration(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> AgentConfigInfo:
    """
    Retrieves the current configuration for a specific agent.

    - **agent_name**: The name of the agent whose configuration is requested.

    Communicates with the Orchestrator.
    Requires an active user session.
    Raises HTTP 404 if the agent or its configuration is not found.
    """
    config = crud_agent.get_agent_config(name=agent_name)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"Config not found for agent '{agent_name}' or failed to retrieve.",
        )
    # AgentConfigInfo allows extra fields, suitable for flexible config structures
    return AgentConfigInfo(**config)


@router.post(
    "/{agent_name}/dispatch",
    response_model=AgentDispatchResponse,
    summary="Dispatch Message to Agent",
)
def dispatch_message_to_agent(
    agent_name: str,
    payload: AgentDispatchPayload,
    current_user: User = Depends(dependencies.get_current_active_user),
) -> AgentDispatchResponse:
    """
    Sends a message or command to a specific agent via the Orchestrator.

    - **agent_name**: The target agent's name.
    - **payload**: Contains the message and optional context.

    Includes user information as the originator.
    Requires an active user session.
    Raises HTTP 404 if the agent is not found.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    logger.info(
        f"User '{current_user.username}' dispatching message to agent '{agent_name}'."
    )

    orchestrator_payload = {
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
            logger.warning(f"Agent '{agent_name}' not found for dispatch.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found.",
            )
        else:
            logger.error(
                f"Orchestrator response for dispatch_agent_message ('{agent_name}') missing 'response' key."
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response format from orchestrator for agent dispatch.",
            )

    return AgentDispatchResponse(
        agent_name=received_agent_name, response=agent_response, request_id=request_id
    )


@router.post(
    "/{agent_name}/assess",
    response_model=AgentActionResponse,
    summary="Trigger Agent Self-Assessment",
)
def trigger_agent_assessment(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """
    Triggers a self-assessment process for a specific agent.

    - **agent_name**: The name of the agent to assess.

    Communicates with the Orchestrator to initiate the assessment.
    Requires superuser privileges.
    Raises HTTP 404 if the agent is not found.
    Raises HTTP 502 if the orchestrator fails to trigger the assessment.
    """
    logger.info(
        f"Superuser '{current_user.username}' triggering assessment for agent '{agent_name}'."
    )

    orchestrator_payload = {"agent_name": agent_name}

    response_payload = _call_orchestrator(
        action="assess_agent", payload=orchestrator_payload
    )

    status_report = response_payload.get("status", "unknown")
    message = response_payload.get("message")
    received_agent_name = response_payload.get("agent_name", agent_name)
    request_id = response_payload.get("request_id")

    if status_report == "error" and "not found" in (message or "").lower():
        logger.warning(f"Agent '{agent_name}' not found for assessment trigger.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found.",
        )
    elif status_report == "error":
        logger.error(
            f"Orchestrator failed to trigger assessment for '{agent_name}': {message}"
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


# --- Agent Lifecycle Control ---


@router.post(
    "/{agent_name}/start", response_model=AgentActionResponse, summary="Start Agent"
)
def start_agent(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """
    Sends a command to the Orchestrator to start a specific agent.

    - **agent_name**: The name of the agent to start.

    Requires superuser privileges.
    Raises HTTP 404 if the agent is not found.
    Raises HTTP 502 if the orchestrator fails to start the agent.
    """
    logger.info(
        f"Superuser '{current_user.username}' requesting start for agent '{agent_name}'."
    )
    response = crud_agent.control_agent_lifecycle(agent_name, "start_agent")
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process request.",
        )
    if response.status == "error":
        if "not found" in (response.detail or "").lower():
            raise HTTPException(
                status_code=404,
                detail=response.detail or f"Agent '{agent_name}' not found.",
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=response.detail or "Orchestrator failed to start agent.",
            )
    return response


@router.post(
    "/{agent_name}/stop", response_model=AgentActionResponse, summary="Stop Agent"
)
def stop_agent(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """
    Sends a command to the Orchestrator to stop a specific agent.

    - **agent_name**: The name of the agent to stop.

    Requires superuser privileges.
    Raises HTTP 404 if the agent is not found.
    Raises HTTP 502 if the orchestrator fails to stop the agent.
    """
    logger.info(
        f"Superuser '{current_user.username}' requesting stop for agent '{agent_name}'."
    )
    response = crud_agent.control_agent_lifecycle(agent_name, "stop_agent")
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process request.",
        )
    if response.status == "error":
        if "not found" in (response.detail or "").lower():
            raise HTTPException(
                status_code=404,
                detail=response.detail or f"Agent '{agent_name}' not found.",
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=response.detail or "Orchestrator failed to stop agent.",
            )
    return response


@router.post(
    "/{agent_name}/restart", response_model=AgentActionResponse, summary="Restart Agent"
)
def restart_agent(
    agent_name: str,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """
    Sends a command to the Orchestrator to restart a specific agent.

    - **agent_name**: The name of the agent to restart.

    Requires superuser privileges.
    Raises HTTP 404 if the agent is not found.
    Raises HTTP 502 if the orchestrator fails to restart the agent.
    """
    logger.info(
        f"Superuser '{current_user.username}' requesting restart for agent '{agent_name}'."
    )
    response = crud_agent.control_agent_lifecycle(agent_name, "restart_agent")
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process request.",
        )
    if response.status == "error":
        if "not found" in (response.detail or "").lower():
            raise HTTPException(
                status_code=404,
                detail=response.detail or f"Agent '{agent_name}' not found.",
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=response.detail or "Orchestrator failed to restart agent.",
            )
    return response


@router.put(
    "/{agent_name}/config",
    response_model=AgentActionResponse,
    summary="Update Agent Configuration",
)
def update_agent_configuration(
    agent_name: str,
    config_data: AgentConfigUpdate,
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """
    Updates the configuration for a specific agent via the Orchestrator.

    - **agent_name**: The name of the agent to update.
    - **config_data**: The new configuration settings.

    Communicates with the Orchestrator.
    Requires superuser privileges.
    Raises HTTP 404 if the agent is not found.
    Raises HTTP 502 if communication with the orchestrator fails.
    """
    logger.info(
        f"User '{current_user.username}' updating config for agent '{agent_name}'."
    )

    # Call the CRUD operation with corrected parameter names
    updated_config_response = crud_agent.update_agent_config(
        agent_name=agent_name,
        config_in=config_data,  # Corrected: agent_name, config_in
    )

    if updated_config_response is None:
        # This case implies the agent might not have been found by the orchestrator,
        # or another error occurred during the orchestrator call handled within crud_agent.
        logger.warning(
            f"Failed to update config for agent '{agent_name}' via orchestrator (crud returned None)."
        )
        # crud_agent.update_agent_config now returns Optional[Dict[str, Any]]
        # We need to decide what AgentActionResponse to return here.
        # Let's assume if crud_agent returns None, it's an issue communicated by orchestrator
        # or the agent wasn't found by it.
        # Raising an HTTPException might be more appropriate if crud_agent can't find the agent
        # or if the response from orchestrator indicates a clear error.
        # For now, let's return an error status in AgentActionResponse.
        return AgentActionResponse(
            agent_name=agent_name,
            action="update_config",
            status="error",
            detail=f"Failed to update config for agent '{agent_name}'. Orchestrator did not confirm update or agent not found.",
        )

    # If crud_agent.update_agent_config was successful, it returns the new config dict.
    # The endpoint is expected to return AgentActionResponse.
    # We infer success if updated_config_response is not None.
    return AgentActionResponse(
        agent_name=agent_name,
        action="update_config",
        status="success",  # Assuming success if crud_agent returned a config
        detail=f"Configuration for agent '{agent_name}' update process initiated.",
        data=updated_config_response,  # Include the new config if available
    )


@router.post(
    "/reload",
    response_model=AgentActionResponse,
    summary="Reload All Agent Configurations",
)
def reload_all_agents_configs(
    current_user: User = Depends(dependencies.get_current_active_superuser),
) -> AgentActionResponse:
    """Triggers a reload of all agent configurations via the Orchestrator.

    This typically involves the Orchestrator re-reading configuration files.
    Requires superuser privileges.
    Raises HTTP 502 if the orchestrator fails to reload configurations.
    """
    logger.info(
        f"Superuser '{current_user.username}' requesting reload of all agent configurations."
    )
    response = crud_agent.reload_agent_configurations()
    if response is None:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with orchestrator or process reload request.",
        )
    if response.status == "error":
        raise HTTPException(
            status_code=502,
            detail=response.detail or "Orchestrator failed to reload configurations.",
        )
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

