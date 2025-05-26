"""Demo API endpoints for WebUI (no authentication required)."""

import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.utils.file_operations import (
    load_prompt,
    save_prompt,
    list_available_agents,
    get_all_prompts,
)

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


@router.get("/agents", summary="List all available agents (demo)")
def list_agents_demo() -> Dict[str, List[str]]:
    """Get list of all agents with available prompts (demo mode - no auth)."""
    try:
        agents = list_available_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list agents"
        )


@router.get("/prompts", summary="Get all prompts (demo)")
def get_all_prompts_demo() -> Dict[str, str]:
    """Get all prompts as a dictionary mapping agent names to content (demo mode - no auth)."""
    try:
        return get_all_prompts()
    except Exception as e:
        logger.error(f"Error getting all prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prompts"
        )


@router.get("/prompts/{agent_name}", response_model=PromptResponse, summary="Get specific agent prompt (demo)")
def get_prompt_demo(agent_name: str) -> PromptResponse:
    """Get prompt content for a specific agent (demo mode - no auth)."""
    content = load_prompt(agent_name)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt not found for agent: {agent_name}"
        )

    return PromptResponse(agent_name=agent_name, content=content)


@router.put("/prompts/{agent_name}", summary="Update agent prompt (demo)")
def update_prompt_demo(
    agent_name: str,
    prompt_data: PromptUpdate,
) -> Dict[str, str]:
    """Update prompt content for a specific agent (demo mode - no auth)."""
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


@router.post("/prompts", status_code=status.HTTP_201_CREATED, summary="Create new agent prompt (demo)")
def create_prompt_demo(prompt_data: PromptCreate) -> Dict[str, str]:
    """Create a new prompt for an agent (demo mode - no auth)."""
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
