from __future__ import annotations

import logging
import os

# ruff: noqa: N999
from dataclasses import dataclass
from typing import Any, Optional

# Optional import for Discord.py
try:
    import discord

    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

from .Middleware import Middleware
from .schemas import InternalRequest

logger = logging.getLogger(__name__)


@dataclass
class ParsedCommand:
    command: str
    args: dict[str, Any]
    user: str


def parse_command(text: str) -> ParsedCommand:
    parts = text.strip().split()
    command = parts[0] if parts else ""
    args = {"raw": " ".join(parts[1:])}
    user = "anonymous"
    return ParsedCommand(command=command, args=args, user=user)


def determine_agent(channel_id: str, command: str) -> str:
    mapping = {"!metrics": "metrics"}
    return mapping.get(command, "metrics")


class DiscordAdapter:
    """Minimal adapter between Discord messages and the pipeline."""

    # Class-level Discord client
    _discord_client: Optional[Any] = None

    @classmethod
    def get_discord_client(cls) -> Optional[Any]:
        """
        Get or create a Discord client instance.

        Returns:
            The Discord client or None if Discord is not available.
        """
        if not DISCORD_AVAILABLE:
            return None

        if cls._discord_client is None:
            token = os.getenv("DISCORD_TOKEN")
            if token:
                intents = discord.Intents.default()
                intents.message_content = True
                cls._discord_client = discord.Client(intents=intents)
            else:
                logger.warning("DISCORD_TOKEN not found in environment variables")

        return cls._discord_client

    @staticmethod
    def on_message_receive(raw_text: str, channel_id: str) -> None:
        parsed = parse_command(raw_text)
        target_agent = determine_agent(channel_id, parsed.command)
        request = InternalRequest(
            user_id=parsed.user,
            command=parsed.command,
            args=parsed.args,
            channel=channel_id,
            agent_key=target_agent,
        )
        Middleware.process(request)

    @staticmethod
    async def send_message(channel_id: str, text: str) -> None:
        """
        Send a message to a Discord channel.

        Args:
            channel_id: The ID of the Discord channel to send the message to.
            text: The message content to send.

        Returns:
            None
        """
        # Fallback to console output if Discord is not available
        if not DISCORD_AVAILABLE:
            logger.info(f"[Discord:{channel_id}] {text}")
            return

        client = DiscordAdapter.get_discord_client()
        if not client:
            logger.info(f"[Discord:{channel_id}] {text}")
            return

        try:
            # Convert channel_id to integer if it's a string
            channel_id_int = (
                int(channel_id) if isinstance(channel_id, str) else channel_id
            )

            # Get the channel by ID
            channel = client.get_channel(channel_id_int)
            if not channel:
                logger.warning(f"Discord channel not found: {channel_id}")
                logger.info(f"[Discord:{channel_id}] {text}")
                return

            # Send the message
            await channel.send(text)
            logger.debug(f"Message sent to Discord channel {channel_id}")

        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            # Fallback to console
            logger.info(f"[Discord:{channel_id}] {text}")
