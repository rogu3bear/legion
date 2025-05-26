"""API endpoints for prompt management."""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from core.utils.file_operations import (
    get_all_prompts,
    list_available_agents,
    load_prompt,
    save_prompt,
)
from interface.dependencies import get_current_active_user
from interface.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class PromptResponse(BaseModel):
    """Response model for prompt data."""
    agent_name: str
    content: str


class PromptUpdate(BaseModel):
    """Request model for updating prompt content."""
    content: str


class PromptCreate(BaseModel):
    """Request model for creating new prompt."""
    agent_name: str
    content: str


@router.get("/", summary="List all available prompts")
def list_prompts(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, List[str]]:
    """Get list of all agents with available prompts."""
    try:
        agents = list_available_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list prompts"
        )


@router.get("/all", summary="Get all prompts")
def get_all_prompts_endpoint(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Get all prompts as a dictionary mapping agent names to content."""
    try:
        return get_all_prompts()
    except Exception as e:
        logger.error(f"Error getting all prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prompts"
        )


@router.get("/{agent_name}", response_model=PromptResponse, summary="Get specific agent prompt")
def get_prompt(
    agent_name: str,
    current_user: User = Depends(get_current_active_user),
) -> PromptResponse:
    """Get prompt content for a specific agent."""
    content = load_prompt(agent_name)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt not found for agent: {agent_name}"
        )

    return PromptResponse(agent_name=agent_name, content=content)


@router.put("/{agent_name}", summary="Update agent prompt")
def update_prompt(
    agent_name: str,
    prompt_data: PromptUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Update prompt content for a specific agent."""
    success = save_prompt(agent_name, prompt_data.content)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save prompt for agent: {agent_name}"
        )

    return {
        "message": f"Prompt updated successfully for agent: {agent_name}",
        "agent_name": agent_name
    }


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create new agent prompt")
def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Create a new prompt for an agent."""
    # Check if prompt already exists
    existing_content = load_prompt(prompt_data.agent_name)
    if existing_content is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Prompt already exists for agent: {prompt_data.agent_name}"
        )

    success = save_prompt(prompt_data.agent_name, prompt_data.content)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prompt for agent: {prompt_data.agent_name}"
        )

    return {
        "message": f"Prompt created successfully for agent: {prompt_data.agent_name}",
        "agent_name": prompt_data.agent_name
    }
