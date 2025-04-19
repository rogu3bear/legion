"""
Feed renderer for agent posts.
"""
import discord
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

# Color mapping for different message types
COLOR_MAP = {
    MessageType.INFO: discord.Color.blue(),
    MessageType.WARNING: discord.Color.gold(),
    MessageType.ERROR: discord.Color.red(),
    MessageType.SUCCESS: discord.Color.green()
}

def render_feed_item(agent_name, message, msg_type=MessageType.INFO, fields=None):
    """
    Create a Discord embed for an agent message.
    
    Args:
        agent_name (str): Name of the agent
        message (str): Main message content
        msg_type (MessageType): Type of message for color coding
        fields (list): Optional list of (name, value) tuples for additional fields
    
    Returns:
        discord.Embed: Formatted message embed
    """
    embed = discord.Embed(
        title=agent_name,
        description=message,
        color=COLOR_MAP.get(msg_type, discord.Color.default()),
        timestamp=datetime.utcnow()
    )
    
    # Add any additional fields
    if fields:
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
            
    # Set footer with timestamp
    embed.set_footer(text=f"Posted at {embed.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    return embed

def render_error(agent_name, error_msg, details=None):
    """
    Create an error message embed.
    
    Args:
        agent_name (str): Name of the agent
        error_msg (str): Error message
        details (str): Optional detailed error information
    """
    fields = [("Error Details", details)] if details else None
    return render_feed_item(agent_name, error_msg, MessageType.ERROR, fields)

def render_success(agent_name, message, metrics=None):
    """
    Create a success message embed.
    
    Args:
        agent_name (str): Name of the agent
        message (str): Success message
        metrics (dict): Optional metrics to display
    """
    fields = [(k, str(v)) for k, v in metrics.items()] if metrics else None
    return render_feed_item(agent_name, message, MessageType.SUCCESS, fields)
