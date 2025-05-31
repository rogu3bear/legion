"""Agent related Pydantic schemas for API requests/responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Represents the runtime status and core info of an agent
# fetched from the Legion Orchestrator.
class AgentStatusInfo(BaseModel):
    name: str = Field(..., description="Unique name of the agent.")
    type: str = Field(
        ..., description="Type or class of the agent (e.g., 'ArchitectAgent')."
    )
    status: str = Field(
        description="Current operational status (e.g., 'ONLINE', 'OFFLINE', 'BUSY', 'ERROR')."
    )
    is_active: bool = Field(
        ..., description="Indicates if the agent is currently active and processing."
    )
    capabilities: List[str] = Field(
        [], description="List of capabilities or functions the agent supports."
    )
    last_heartbeat: Optional[datetime] = Field(
        None, description="Timestamp of the last heartbeat received from the agent."
    )
    tags: Optional[List[str]] = Field(
        [], description="List of tags associated with the agent."
    )
    task_owner: Optional[str] = Field(
        None, description="Identifier of the task owner, if any."
    )
    model_config = ConfigDict(
        from_attributes=True
    )  # Allow mapping from ORM objects if applicable


# Schema for representing agent configuration details
# This should align with the structure returned by the Orchestrator/Core
class AgentConfigInfo(BaseModel):
    model: Optional[str] = Field(
        None, description="Default LLM model used by the agent."
    )
    temperature: Optional[float] = Field(
        None, description="Default sampling temperature for LLM responses."
    )
    max_tokens: Optional[int] = Field(
        None, description="Default maximum tokens for LLM responses."
    )
    # Add other core config fields as needed
    # Example: system_prompt: Optional[str] = None
    model_config = ConfigDict(
        extra="allow"
    )  # Allow extra fields defined in agent's YAML config


# --- Schemas below might be needed for Write APIs (Phase 3) ---
# Base schema for creating/updating agents via API (if supported later)
class AgentAPIBase(BaseModel):
    """Base schema for API-based agent management (Future Use)."""

    name: str = Field(..., description="Unique name for the agent.")
    type: str = Field(..., description="Agent class or type identifier.")
    config: Optional[Dict[str, Any]] = Field(
        {}, description="Agent-specific configuration dictionary."
    )
    # Note: status, capabilities, is_active are runtime, not set via API directly


class AgentAPICreate(AgentAPIBase):
    """Schema for creating an agent via API (Future Use)."""

    pass


class AgentAPIUpdate(BaseModel):
    """Schema for updating an agent via API (Future Use)."""

    # Allow updating specific fields
    config: Optional[Dict[str, Any]] = Field(
        None, description="New agent configuration settings."
    )
    is_active: Optional[bool] = Field(
        None, description="New activation status."
    )  # Allow activating/deactivating


# ---------------------------------------------------------------------------
# Compatibility aliases for legacy import paths (e.g., interface.api.v1.schemas)
# ---------------------------------------------------------------------------
class AgentCreate(AgentAPIBase):
    """Backward-compat alias mapping to AgentAPICreate for legacy imports."""

    pass


class AgentUpdate(AgentAPIUpdate):
    """Backward-compat alias mapping to AgentAPIUpdate for legacy imports."""

    pass


# --- Schemas for legacy DB model interaction (might be deprecated) ---
# Kept for reference, but API should likely return AgentStatusInfo
class AgentDBBase_Legacy(BaseModel):
    name: Optional[str] = None  # Name made Optional to match AgentDBUpdate_Legacy
    description: Optional[str] = None
    model: Optional[str] = None  # Made Optional to match AgentDBUpdate_Legacy
    temperature: Optional[float] = 0.7  # Made Optional
    max_tokens: Optional[int] = 2000  # Made Optional
    is_active: Optional[bool] = True  # Made Optional
    config: Optional[Dict[str, Any]] = None


class AgentDBCreate_Legacy(AgentDBBase_Legacy):
    pass


class AgentDBUpdate_Legacy(AgentDBBase_Legacy):  # This class makes them optional
    name: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class AgentDBInDBBase_Legacy(AgentDBBase_Legacy):
    id: int
    created_at: datetime
    last_active: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class AgentDB_Legacy(AgentDBInDBBase_Legacy):
    pass


# --- Schemas for Agent Interaction APIs (Dispatch/Action) ---
# These seem relevant for Phase 3, kept here for context


# Schema for dispatching a message TO an agent
class AgentDispatchPayload(BaseModel):
    """Payload for sending a message or command to an agent."""

    message: str = Field(
        ..., description="The text message or command to send to the agent."
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Optional additional context data for the agent."
    )
    tags: Optional[List[str]] = Field(
        None, description="Optional list of tags to attach to the dispatch."
    )
    task_owner: Optional[str] = Field(
        None, description="Identifier for the owner of the dispatched task."
    )
    payload: Optional[Dict[str, Any]] = Field(
        None, description="Arbitrary payload for the agent action."
    )


# Schema for the response FROM an agent dispatch
class AgentDispatchResponse(BaseModel):
    """Response received after dispatching a message to an agent."""

    agent_name: str = Field(..., description="The name of the agent that responded.")
    response: str = Field(..., description="The text response received from the agent.")
    request_id: Optional[str] = Field(
        None, description="Unique identifier for the request, if available."
    )
    message: Optional[str] = Field(
        None, description="Optional supplementary message from the orchestrator."
    )


# Schema for simple action responses (like assess, start/stop)
class AgentActionResponse(BaseModel):
    """Standard response format for agent lifecycle or action requests."""

    agent_name: str = Field(
        ..., description="The name of the agent the action was performed on."
    )
    action: str = Field(
        description="The action that was requested (e.g., 'start_agent', 'assess_agent')."
    )
    status: str = Field(
        ..., description="Outcome status of the action ('success' or 'error')."
    )
    detail: Optional[str] = Field(
        None, description="Additional details or error message."
    )


# Schema for updating agent configuration via PUT request
class AgentConfigUpdate(BaseModel):
    """Payload for updating an agent's configuration. Allows partial updates."""

    config: Dict[str, Any] = Field(
        description="A dictionary containing the configuration key-value pairs to update."
    )


class AgentRegisterRequest(BaseModel):
    """Payload used by agents to register with the orchestrator."""

    id: str = Field(..., description="Unique agent identifier")
    role: str = Field(..., description="Declared agent role")
    capabilities: List[str] = Field(default_factory=list)


class AgentRegisterResponse(BaseModel):
    token: str = Field(..., description="Authentication token issued to the agent")
