from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, constr, validator
from typing import List, Dict, Any
import redis.exceptions
import html

# Assuming prompt_repo is structured to have these functions
# and get_redis_client is available to be injected or repo functions handle client internally.
from data.prompt_repo import (
    all_agents as repo_all_agents,
    get_prompt as repo_get_prompt,
    save_prompt as repo_save_prompt,
    revert_prompt as repo_revert_prompt,
    get_all_skills as repo_get_all_skills,
    get_redis_client # To catch ConnectionError early if needed
)

# New router prefix
router = APIRouter(prefix="/api/admin/prompts", tags=["admin_prompts"])

class PromptData(BaseModel):
    system: str
    skills: List[str]

class PromptUpdate(BaseModel):
    system: constr(strip_whitespace=True, min_length=5, max_length=8000)
    skills: List[str] # Will be validated against all_skills

    @validator('system')
    def prevent_dangerous_html(cls, value):
        # Basic check, consider a more robust sanitizer if complex HTML is ever expected.
        # For now, we mainly rely on html.escape before storage.
        # This validator is more about preventing obviously malicious script tags if any.
        if '<script' in value.lower():
            raise ValueError('System prompt cannot contain script tags.')
        return value

# Dependency to get a Redis client and handle connection errors globally for this router
async def get_db_client():
    try:
        client = get_redis_client()
        if client is None: # Should not happen if get_redis_client raises
            raise redis.exceptions.ConnectionError("Redis client could not be initialized.")
        client.ping() # Verify connection
        return client
    except redis.exceptions.ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "Redis unavailable", "message": str(e)}
        )

@router.get("", summary="List all agents and master skill list")
async def get_agents_and_skills(client: redis.Redis = Depends(get_db_client)):
    """
    Return full agent registry list with current system prompts (Redis or default)
    and a master list of all unique skills.
    """
    try:
        agents_data = repo_all_agents(client)
        master_skills = repo_get_all_skills(client)
        return {
            "agents": agents_data,
            "all_skills": master_skills
        }
    except redis.exceptions.ConnectionError as e: # Should be caught by Depends, but as a fallback
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error": "Redis unavailable", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch agents: {str(e)}")

@router.get("/{agent}", response_model=PromptData, summary="Get current prompt for an agent")
async def get_agent_prompt_route(agent: str, client: redis.Redis = Depends(get_db_client)):
    """Fetch system prompt and skills for a specific agent (Redis override or default)."""
    try:
        system_prompt, skills = repo_get_prompt(client, agent)
        # Ensure agent exists in the registry, even if no specific prompt override in Redis
        registry_agents = repo_all_agents(client) #This is a bit inefficient, ideally get_prompt would signal if agent is unknown
        if agent not in registry_agents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent}' not found in registry.")

        return PromptData(system=system_prompt, skills=skills)
    except redis.exceptions.ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error": "Redis unavailable", "message": str(e)})
    except Exception as e:
        # Catch if repo_get_prompt or all_agents raises other specific errors for "not found"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch prompt for {agent}: {str(e)}")


@router.put("/{agent}", summary="Update agent prompt and skills")
async def update_agent_prompt_route(agent: str, prompt_data: PromptUpdate, client: redis.Redis = Depends(get_db_client)):
    """Update system prompt and skills for a specific agent. Validates skills against master list."""
    try:
        # Validate agent existence
        agents_data = repo_all_agents(client)
        if agent not in agents_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent}' not found.")

        master_skills = set(repo_get_all_skills(client))
        for skill in prompt_data.skills:
            if skill not in master_skills:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid skill: '{skill}'. Skill must be one of {sorted(list(master_skills))}"
                )

        # System prompt is already validated by Pydantic for length and basic script tag check.
        # html.escape will be handled by save_prompt in the repo.
        saved_data = repo_save_prompt(client, agent, prompt_data.system, prompt_data.skills)
        return {
            "status": "success",
            "message": f"Prompt updated for agent {agent}",
            "updated_prompt": {"system": html.unescape(saved_data['system']), "skills": saved_data['skills']}
        }
    except redis.exceptions.ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error": "Redis unavailable", "message": str(e)})
    except HTTPException: # Re-raise if it's already an HTTPException (like 422 from skill validation)
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update prompt for {agent}: {str(e)}")

@router.post("/{agent}/revert", summary="Revert agent prompt to previous version")
async def revert_agent_prompt_route(agent: str, client: redis.Redis = Depends(get_db_client)):
    """Reverts the agent's prompt and skills to the last saved version from history."""
    try:
        # Validate agent existence
        agents_data = repo_all_agents(client)
        if agent not in agents_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent}' not found.")

        reverted_data = repo_revert_prompt(client, agent)
        if reverted_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No history found for agent {agent} to revert.")

        return {
            "status": "success",
            "message": f"Prompt for agent {agent} reverted to previous version.",
            "reverted_prompt": reverted_data # system is already unescaped by repo
        }
    except redis.exceptions.ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error": "Redis unavailable", "message": str(e)})
    except HTTPException: # Re-raise if it's already an HTTPException
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to revert prompt for {agent}: {str(e)}")
