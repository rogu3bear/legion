"""
Legion system tools for agent collaboration, memory, and Discord integration.
"""
import os
import glob
import yaml
import logging
from typing import Dict, List, Optional, Any
from src.legion_memory import LegionAgentMemory
from src.indexing import index_documents, search
from src.ux_feed import render_feed_item, render_error, render_success, MessageType

# Configure logging
logger = logging.getLogger(__name__)

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

class LegionTools:
    """Tools for integrating Legion functionality: memory, search, code edit, Discord messaging."""
    
    def __init__(self):
        self.memory = LegionAgentMemory()
        self.index = index_documents("docs/")
        logger.info("Legion tools initialized with document index")
    
    def file_search(self, query: str) -> List[Dict[str, str]]:
        """
        Search for files containing the query.
        
        Args:
            query: The search query
            
        Returns:
            List of dictionaries with file paths and content snippets
        """
        logger.info(f"Searching for: {query}")
        results = search(query, self.index)
        return [{"file": file, "content": content} for file, content in results]
    
    def code_edit(self, file_path: str, instructions: str) -> Dict[str, Any]:
        """
        Edit a code file based on instructions.
        
        Args:
            file_path: Path to the file to edit
            instructions: Instructions for the edit
            
        Returns:
            Dictionary with success status and message
        """
        logger.info(f"Editing file: {file_path}")
        # In a real implementation, this would use the edit_file tool
        # For now, we'll just return a success message
        return {
            "success": True,
            "message": f"File {file_path} would be edited according to: {instructions}"
        }
    
    def terminal_cmd(self, command: str) -> Dict[str, Any]:
        """
        Execute a terminal command.
        
        Args:
            command: The command to execute
            
        Returns:
            Dictionary with success status and output
        """
        logger.info(f"Executing command: {command}")
        # In a real implementation, this would use the run_terminal_cmd tool
        # For now, we'll just return a success message
        return {
            "success": True,
            "output": f"Command '{command}' would be executed"
        }
    
    def send_discord_message(self, agent_name: str, message: str, msg_type: str = "info", fields: Optional[List[tuple]] = None) -> Dict[str, Any]:
        """
        Send a message to Discord.
        
        Args:
            agent_name: Name of the agent sending the message
            message: The message content
            msg_type: Type of message (info, warning, error, success)
            fields: Optional list of (name, value) tuples for additional fields
            
        Returns:
            Dictionary with success status and message
        """
        logger.info(f"Sending Discord message from {agent_name}: {message}")
        # In a real implementation, this would use the send_discord_message function
        # For now, we'll just return a success message
        return {
            "success": True,
            "message": f"Message sent to Discord: {message}"
        } 