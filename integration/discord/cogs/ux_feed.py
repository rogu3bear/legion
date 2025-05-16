"""
Feed renderer for agent posts.
"""

from datetime import datetime, timezone
from enum import Enum

import discord


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
    MessageType.SUCCESS: discord.Color.green(),
}


def render_feed_item(agent_name, message, msg_type=MessageType.INFO, fields=None):
    """Creates a Discord embed for an agent message."""
    embed = discord.Embed(
        title=agent_name,
        description=message,
        color=COLOR_MAP.get(msg_type, discord.Color.default()),
        timestamp=datetime.now(timezone.utc),
    )

    # Add any additional fields
    if fields:
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

    # Set footer with timestamp
    embed.set_footer(
        text=f"Posted at {embed.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    return embed


def render_error(agent_name, error_msg, details=None):
    """Creates an error message embed."""
    fields = [("Error Details", details)] if details else None
    return render_feed_item(agent_name, error_msg, MessageType.ERROR, fields)


def render_success(agent_name, message, metrics=None):
    """Creates a success message embed."""
    fields = [(k, str(v)) for k, v in metrics.items()] if metrics else None
    return render_feed_item(agent_name, message, MessageType.SUCCESS, fields)


def render_info(
    agent_name: str, message: str, fields: list[tuple[str, str]] | None = None
):
    """Creates an info message embed."""
    return render_feed_item(agent_name, message, MessageType.INFO, fields)


def render_warning(
    agent_name: str, message: str, fields: list[tuple[str, str]] | None = None
):
    """Creates a warning message embed."""
    return render_feed_item(agent_name, message, MessageType.WARNING, fields)


# render_message can be an alias or a more generic function if needed
# For now, let's make it an alias for render_info for compatibility if tests expect it.
def render_message(
    agent_name: str, message: str, fields: list[tuple[str, str]] | None = None
):
    """Alias for render_info for general message rendering."""
    return render_info(agent_name, message, fields)


"""UX feed cog stub for Discord integration."""
