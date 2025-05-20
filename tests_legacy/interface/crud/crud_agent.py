"""Agent related CRUD operations."""

import logging
from typing import Any, Dict, List, Optional, cast

from sqlalchemy import select  # Added for consistency
from sqlalchemy.orm import Session

from interface.models.agent import Agent  # Updated path

# Assuming communication layer setup
from interface.orchestrator_comm import send_orchestrator_request
from interface.schemas.agent import (
    AgentActionResponse,
    AgentConfigUpdate,
    AgentCreate,
    AgentDispatchPayload,  # Added import for dispatch payload
    AgentStatusInfo,
    AgentUpdate,
)

logger = logging.getLogger(__name__)


def get_agent(db: Session, agent_id: int) -> Optional[Agent]:
    """Fetches an agent by its ID."""
    return cast(Optional[Agent], db.get(Agent, agent_id))


def get_agent_by_name(name: str) -> Optional[AgentStatusInfo]:
    """Retrieve detailed status for a specific agent from the Orchestrator."""
    try:
        response = send_orchestrator_request(
            {"action": "get_agent_status", "agent_name": name}
        )
        if response and response.get("status") == "success" and "agent" in response:
            # Validate and parse the response into AgentStatusInfo object
            agent_data = response["agent"]  # Assuming response['agent'] is a dict
            return AgentStatusInfo(**agent_data)
        else:
            logger.error(
                f"Failed to get agent status for '{name}'. Response: {response}"
            )
            return None
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for get_agent_status({name}): {e}"
        )
        return None


def get_agents(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Agent]:  # Added pagination
    """Retrieve agents with pagination."""
    return cast(
        List[Agent], db.execute(select(Agent).offset(skip).limit(limit)).scalars().all()
    )


def create_agent(db: Session, agent_in: AgentCreate) -> Agent:  # Removed *
    """Create a new agent."""
    db_agent = Agent(**agent_in.dict())  # Simplified creation
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(
    db: Session,
    db_agent: Agent,
    agent_in: AgentUpdate,  # Removed *
) -> Agent:
    """Update an agent."""
    update_data = agent_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(
    db: Session, agent_id: int
) -> Optional[Agent]:  # Changed signature to use ID
    """Delete an agent by ID."""
    db_agent = cast(Optional[Agent], db.get(Agent, agent_id))
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return db_agent
    return None


# --- Read Operations (Fetching data from Orchestrator) ---


def get_all_agents_status() -> List[AgentStatusInfo]:
    """Retrieve list of all agents and their status from the Orchestrator."""
    try:
        response = send_orchestrator_request({"action": "list_agents"})
        if response and response.get("status") == "success" and "agents" in response:
            # Validate and parse the response into AgentStatusInfo objects
            agents_data = response[
                "agents"
            ]  # Assuming response['agents'] is a list of dicts
            agent_list = [AgentStatusInfo(**agent_data) for agent_data in agents_data]
            return agent_list
        else:
            logger.error(
                f"Failed to list agents from orchestrator. Response: {response}"
            )
            return []
    except Exception as e:
        logger.exception(f"Error communicating with orchestrator for list_agents: {e}")
        return []


def get_agent_config(name: str) -> Optional[Dict[str, Any]]:
    """Retrieve configuration for a specific agent from the Orchestrator."""
    # This assumes the orchestrator has an action to fetch config
    try:
        response = send_orchestrator_request(
            {"action": "get_agent_config", "agent_name": name}
        )
        if response and response.get("status") == "success" and "config" in response:
            return cast(Dict[str, Any], response["config"])
        else:
            logger.error(
                f"Failed to get agent config for '{name}'. Response: {response}"
            )
            return None
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for get_agent_config({name}): {e}"
        )
        return None


# --- Write Operations (Placeholder - To be implemented in Phase 3) ---
# These would interact with the orchestrator to create/update/delete
# or modify agent states (start/stop/assess).

# def create_agent(...) -> AgentStatusInfo:
#     # Send command to orchestrator to load/create agent
#     pass

# def update_agent(...) -> AgentStatusInfo:
#     # Send command to orchestrator to update config/state
#     pass

# def delete_agent(...) -> bool:
#     # Send command to orchestrator to unload/delete agent
#     pass


def get_agent_status(agent_name: str) -> Optional[AgentStatusInfo]:
    """Retrieve the status of a specific agent from the Orchestrator."""
    try:
        response = send_orchestrator_request(
            {"action": "get_agent_status", "agent_name": agent_name}
        )
        if response and response.get("status") == "success" and "agent" in response:
            agent_data = response["agent"]
            return AgentStatusInfo(**agent_data)
        else:
            logger.error(
                f"Failed to get agent status for '{agent_name}'. Response: {response}"
            )
            return None
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for get_agent_status({agent_name}): {e}"
        )
        return None


def update_agent_config(
    agent_name: str, config_in: AgentConfigUpdate
) -> Optional[Dict[str, Any]]:
    """Update the configuration of a specific agent via the Orchestrator."""
    try:
        response = send_orchestrator_request(
            {
                "action": "update_agent_config",
                "agent_name": agent_name,
                "config": config_in.dict(),
            }
        )
        if response and response.get("status") == "success" and "config" in response:
            return cast(Dict[str, Any], response["config"])
        else:
            logger.error(
                f"Failed to update agent config for '{agent_name}'. Response: {response}"
            )
            return None
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for update_agent_config({agent_name}): {e}"
        )
        return None


def dispatch_to_agent(
    agent_name: str, message: AgentDispatchPayload
) -> Optional[Dict[str, Any]]:
    """Dispatch a message or task to a specific agent via the Orchestrator."""
    try:
        response = send_orchestrator_request(
            {
                "action": "dispatch_to_agent",
                "agent_name": agent_name,
                "payload": message.model_dump(),  # Use model_dump for Pydantic v2
            }
        )
        return response
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for dispatch_to_agent({agent_name}): {e}"
        )
        return None


def assess_agent(agent_name: str) -> Optional[Dict[str, Any]]:
    """Trigger a self-assessment for a specific agent via the Orchestrator."""
    try:
        response = send_orchestrator_request(
            {"action": "assess_agent", "agent_name": agent_name}
        )
        return response
    except Exception as e:
        logger.exception(
            f"Error communicating with orchestrator for assess_agent({agent_name}): {e}"
        )
        return None


def control_agent_lifecycle(
    agent_name: str, lifecycle_action: str
) -> Optional[AgentActionResponse]:
    """Sends a lifecycle control action (start, stop, restart) to the Orchestrator."""
    valid_actions = ["start_agent", "stop_agent", "restart_agent"]
    if lifecycle_action not in valid_actions:
        logger.error(f"Invalid lifecycle action requested: {lifecycle_action}")
        return AgentActionResponse(
            agent_name=agent_name,
            action=lifecycle_action,
            status="error",
            detail="Invalid action",
        )

    command = {"action": lifecycle_action, "payload": {"agent_name": agent_name}}
    response = send_orchestrator_request(command)

    if response and "status" in response:
        return AgentActionResponse(
            agent_name=agent_name,
            action=lifecycle_action,
            status=response["status"],
            detail=response.get("detail"),
        )
    else:
        logger.error(
            f"Failed to {lifecycle_action} agent '{agent_name}'. Response: {response}"
        )
        return AgentActionResponse(
            agent_name=agent_name,
            action=lifecycle_action,
            status="error",
            detail="Communication error or invalid response from orchestrator",
        )


def reload_agent_configurations() -> Optional[AgentActionResponse]:
    """Sends a command to reload all agent configurations via the orchestrator."""
    command = {"action": "reload_agent_configs"}
    response_data = send_orchestrator_request(command)

    if response_data and "status" in response_data:
        # Note: AgentActionResponse expects agent_name and action.
        # Since this reloads *all* agents, we might return a generic response
        # or adapt the schema/response structure later.
        return AgentActionResponse(
            agent_name="all",  # Indicate this affects all agents
            action="reload_configs",
            status=response_data["status"],
            detail=response_data.get("detail"),
        )
    else:
        logger.error(f"Failed to reload agent configs. Response: {response_data}")
        return AgentActionResponse(
            agent_name="all",
            action="reload_configs",
            status="error",
            detail="Communication error or invalid response from orchestrator",
        )


# Placeholder for database CRUD if needed later
# Example: crud_agent_db.py
