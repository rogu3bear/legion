"""
File I/O utilities for prompt management.

Provides centralized file operations for Legion prompt templates.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import portalocker
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path("legion/prompts")


def load_prompt(agent_name: str) -> Optional[str]:
    """Load prompt content for a specific agent."""
    prompt_file = PROMPTS_DIR / f"{agent_name}.md"

    try:
        if prompt_file.exists():
            return prompt_file.read_text(encoding='utf-8')
        else:
            logger.warning(f"Prompt file not found: {prompt_file}")
            return None
    except Exception as e:
        logger.error(f"Error loading prompt for {agent_name}: {e}")
        return None


def save_prompt(agent_name: str, content: str) -> bool:
    """Save prompt content for a specific agent with file locking."""
    prompt_file = PROMPTS_DIR / f"{agent_name}.md"

    try:
        # Ensure prompts directory exists
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

        # Open file with exclusive lock
        with open(prompt_file, 'w', encoding='utf-8') as f:
            try:
                # Acquire exclusive lock with timeout
                portalocker.lock(f, portalocker.LOCK_EX | portalocker.LOCK_NB)
                f.write(content)
                logger.info(f"Saved prompt for agent: {agent_name}")
                return True
            except portalocker.LockException:
                logger.error(f"Could not acquire lock for prompt file: {agent_name}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Prompt file is currently being modified by another process: {agent_name}"
                )
            finally:
                # Lock is automatically released when file is closed
                pass
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error saving prompt for {agent_name}: {e}")
        return False


def list_available_agents() -> List[str]:
    """List all agents with existing prompt files."""
    try:
        if not PROMPTS_DIR.exists():
            return []

        agent_names = []
        for prompt_file in PROMPTS_DIR.glob("*.md"):
            agent_names.append(prompt_file.stem)

        return sorted(agent_names)
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return []


def get_all_prompts() -> Dict[str, str]:
    """Get all prompts as a dictionary mapping agent names to content."""
    prompts = {}
    agents = list_available_agents()

    for agent in agents:
        content = load_prompt(agent)
        if content is not None:
            prompts[agent] = content

    return prompts
