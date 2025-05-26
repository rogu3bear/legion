"""Discord bridge utility for Legion.

This module provides Discord messaging capabilities that can be used:
1. Standalone for sending messages/actions
2. Integrated with the orchestrator's message routing system
"""

import asyncio
import json
import os
from typing import Any, Dict, Optional

import discord
from dotenv import load_dotenv

from integration.discord.cogs.ux_feed import MessageType, render_feed_item

load_dotenv(override=True)


class DiscordBridge:
    """Bridge for sending messages to Discord channels."""

    def __init__(self, token: Optional[str] = None, channel_id: Optional[int] = None):
        """Initialize the Discord bridge.

        Args:
            token: Discord bot token. If None, uses DISCORD_TOKEN from env
            channel_id: Default channel ID. If None, uses AGENT_FEED_CHANNEL_ID from env
        """
        self.token = token or os.getenv("DISCORD_TOKEN")
        self.channel_id = channel_id or int(os.getenv("AGENT_FEED_CHANNEL_ID", "0"))
        self.intents = discord.Intents.default()
        self.intents.message_content = True

    async def send_message(self, message: str, channel_id: Optional[int] = None) -> bool:
        """Send a simple text message to Discord.

        Args:
            message: The text message to send
            channel_id: Optional channel ID override

        Returns:
            bool: True if message was sent successfully
        """
        return await self.send_action({
            "type": "message",
            "content": message
        }, channel_id)

    async def send_embed(
        self,
        agent_name: str,
        message: str,
        msg_type: MessageType = MessageType.INFO,
        fields: Optional[list] = None,
        channel_id: Optional[int] = None
    ) -> bool:
        """Send a formatted embed message to Discord.

        Args:
            agent_name: Name of the agent sending the message
            message: The message content
            msg_type: Type of message (INFO, WARNING, ERROR, SUCCESS)
            fields: Optional list of (name, value) tuples for embed fields
            channel_id: Optional channel ID override

        Returns:
            bool: True if message was sent successfully
        """
        embed = render_feed_item(agent_name, message, msg_type, fields)

        class EmbedBot(discord.Client):
            def __init__(self, embed_to_send, target_channel_id, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.embed_to_send = embed_to_send
                self.target_channel_id = target_channel_id
                self.success = False

            async def on_ready(self):
                channel = self.get_channel(self.target_channel_id)
                if channel:
                    try:
                        await channel.send(embed=self.embed_to_send)
                        self.success = True
                    except Exception as e:
                        print(f"Error sending embed: {e}")
                await self.close()

        target_id = channel_id or self.channel_id
        client = EmbedBot(embed, target_id, intents=self.intents)

        try:
            await client.start(self.token)
            return client.success
        except Exception as e:
            print(f"Error running embed bot: {e}")
            return False

    async def send_action(self, action: Dict[str, Any], channel_id: Optional[int] = None) -> bool:
        """Send a JSON action to Discord.

        Args:
            action: Dictionary containing the action data
            channel_id: Optional channel ID override

        Returns:
            bool: True if action was sent successfully
        """
        class ActionBot(discord.Client):
            def __init__(self, action_data, target_channel_id, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.action_data = action_data
                self.target_channel_id = target_channel_id
                self.success = False

            async def on_ready(self):
                channel = self.get_channel(self.target_channel_id)
                if channel:
                    try:
                        # Check if action contains a plain message
                        if self.action_data.get("type") == "message":
                            await channel.send(self.action_data.get("content", ""))
                        else:
                            # Send as JSON
                            await channel.send(json.dumps(self.action_data))
                        self.success = True
                    except Exception as e:
                        print(f"Error sending action: {e}")
                await self.close()

        target_id = channel_id or self.channel_id
        client = ActionBot(action, target_id, intents=self.intents)

        try:
            await client.start(self.token)
            return client.success
        except Exception as e:
            print(f"Error running action bot: {e}")
            return False


# Singleton instance for convenience
_bridge = None


def get_discord_bridge() -> DiscordBridge:
    """Get the singleton Discord bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = DiscordBridge()
    return _bridge


# Convenience functions for standalone usage
async def send_discord_message(message: str, channel_id: Optional[int] = None) -> bool:
    """Send a simple message to Discord."""
    bridge = get_discord_bridge()
    return await bridge.send_message(message, channel_id)


async def send_discord_action(action: Dict[str, Any], channel_id: Optional[int] = None) -> bool:
    """Send a JSON action to Discord."""
    bridge = get_discord_bridge()
    return await bridge.send_action(action, channel_id)


async def send_discord_embed(
    agent_name: str,
    message: str,
    msg_type: MessageType = MessageType.INFO,
    fields: Optional[list] = None,
    channel_id: Optional[int] = None
) -> bool:
    """Send a formatted embed to Discord."""
    bridge = get_discord_bridge()
    return await bridge.send_embed(agent_name, message, msg_type, fields, channel_id)


# Orchestrator integration callback
def create_orchestrator_callback(bridge: Optional[DiscordBridge] = None):
    """Create a callback function for the orchestrator's _post_agent_message.

    Args:
        bridge: Optional DiscordBridge instance. If None, uses the singleton

    Returns:
        Async function suitable for orchestrator._post_agent_message
    """
    if bridge is None:
        bridge = get_discord_bridge()

    async def post_agent_message(agent_name: str, payload: Any):
        """Post a message from an agent to Discord."""
        # If payload is already an embed, send it directly
        if isinstance(payload, discord.Embed):
            class EmbedBot(discord.Client):
                def __init__(self, embed, channel_id, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.embed = embed
                    self.channel_id = channel_id

                async def on_ready(self):
                    channel = self.get_channel(self.channel_id)
                    if channel:
                        try:
                            await channel.send(embed=self.embed)
                        except Exception as e:
                            print(f"Error sending orchestrator embed: {e}")
                    await self.close()

            # Try to get agent-specific channel or use default
            channel_id = int(os.getenv(f"{agent_name.upper()}_CHANNEL_ID", bridge.channel_id))
            client = EmbedBot(payload, channel_id, intents=bridge.intents)

            try:
                await client.start(bridge.token)
            except Exception as e:
                print(f"Error in orchestrator callback: {e}")
        else:
            # Otherwise, create a simple info embed
            await bridge.send_embed(agent_name, str(payload))

    return post_agent_message


# Example usage
if __name__ == "__main__":
    async def test():
        # Test simple message
        await send_discord_message("Test message from discord_bridge.py")

        # Test action
        await send_discord_action({
            "type": "test",
            "detail": "bridge operational",
            "source": "discord_bridge.py"
        })

        # Test embed
        await send_discord_embed(
            "TestAgent",
            "This is a test embed message",
            MessageType.SUCCESS,
            fields=[("Status", "Operational"), ("Version", "1.0.0")]
        )

    asyncio.run(test())
