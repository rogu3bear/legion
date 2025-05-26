"""
Centralized File I/O Utility Methods for Legion Prompt Management.

This module provides reusable, lightweight functions for prompt file operations
as requested in the WebUI backend implementation requirements.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Centralized configuration for prompt file locations
PROMPTS_DIR = Path("legion/prompts")
PROMPT_FILE_EXTENSION = ".md"


def load_prompt(agent_name: str) -> str:
    """
    Load prompt content for a specific agent.

    Args:
        agent_name: Name of the agent whose prompt to load

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: If prompt file does not exist
        IOError: If file cannot be read
    """
    prompt_file = PROMPTS_DIR / f"{agent_name}{PROMPT_FILE_EXTENSION}"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found for agent: {agent_name}")

    try:
        content = prompt_file.read_text(encoding="utf-8")
        logger.debug(f"Successfully loaded prompt for agent: {agent_name}")
        return content
    except Exception as e:
        logger.error(f"Error reading prompt file for {agent_name}: {e}")
        raise OSError(f"Failed to read prompt for agent: {agent_name}") from e


def save_prompt(agent_name: str, content: str) -> None:
    """
    Save prompt content for a specific agent.

    Args:
        agent_name: Name of the agent whose prompt to save
        content: Prompt content to save

    Raises:
        IOError: If file cannot be written
    """
    prompt_file = PROMPTS_DIR / f"{agent_name}{PROMPT_FILE_EXTENSION}"

    try:
        # Ensure prompts directory exists
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

        prompt_file.write_text(content, encoding="utf-8")
        logger.info(f"Successfully saved prompt for agent: {agent_name}")

    except Exception as e:
        logger.error(f"Error saving prompt for {agent_name}: {e}")
        raise OSError(f"Failed to save prompt for agent: {agent_name}") from e


def prompt_exists(agent_name: str) -> bool:
    """
    Check if a prompt file exists for the given agent.

    Args:
        agent_name: Name of the agent to check

    Returns:
        True if prompt file exists, False otherwise
    """
    prompt_file = PROMPTS_DIR / f"{agent_name}{PROMPT_FILE_EXTENSION}"
    return prompt_file.exists()


def get_prompt_file_path(agent_name: str) -> Path:
    """
    Get the full file path for an agent's prompt file.

    Args:
        agent_name: Name of the agent

    Returns:
        Path object for the prompt file
    """
    return PROMPTS_DIR / f"{agent_name}{PROMPT_FILE_EXTENSION}"
