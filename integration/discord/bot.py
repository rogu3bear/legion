"""Discord bot for Legion integration."""

import asyncio
import logging
import os
import signal
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from legion.core.logging_config import setup_logging
from legion.orchestrator import Orchestrator, ProcessRunningError

# Enable logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Needed for message content access

logger = logging.getLogger(__name__)

message_processing_lock = asyncio.Lock()
processed_message_ids = set()


async def fetch_thread_history(channel, thread, limit):
    """
    Fetch up to `limit` messages from the given thread (or channel).
    Returns a list of messages, or [] on error (rate-limit, perms, etc.).
    """
    try:
        # If thread is a discord.Thread, use thread.history; else, use channel.history
        history_obj = thread if hasattr(thread, "history") else channel
        messages = []
        history = history_obj.history(limit=limit)
        if hasattr(history, "__await__"):
            history = await history
        async for msg in history:
            messages.append(msg)
        return list(reversed(messages))
    except Exception as e:
        logging.warning(f"[fetch_thread_history] Failed to fetch thread history: {e}")
        return []


class LegionBot(commands.Bot):
    def __init__(self, orchestrator=None, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        super().__init__(*args, command_prefix="!", intents=intents, **kwargs)
        self.agent_tasks = []
        self.orchestrator = orchestrator
        self._shutdown_event = asyncio.Event()
        self.logger = logging.getLogger("discord.bot")
        setup_logging()  # Ensure logging is configured
        self.logger.info("Discord bot initialized", extra={"bot_status": "initialized"})

    async def setup_hook(self):
        # Try to connect to existing orchestrator or create new one
        if not self.orchestrator:
            try:
                self.orchestrator = Orchestrator()
            except ProcessRunningError as e:
                logger.error(f"Failed to create orchestrator: {e}")
                await self.close()
                sys.exit(1)

        # Override the placeholder with a real Discord sender
        self.orchestrator._post_agent_message = self._send_agent_message

        # Add cogs
        from integration.discord.cogs.orchestrator import OrchestratorCog

        await self.add_cog(OrchestratorCog(self, self.orchestrator))

        from legion.discord.commands import LegionCommandCog

        await self.add_cog(LegionCommandCog(self, self.orchestrator))

        await self.tree.sync()

        # Set up signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(
                sig, lambda s=sig: asyncio.create_task(self._handle_signal(s))
            )

    async def _handle_signal(self, sig):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        self._shutdown_event.set()

        # Clean up orchestrator
        if self.orchestrator:
            self.orchestrator._release_lock()

        # Close Discord connection
        await self.close()

    async def _send_agent_message(self, agent, payload):
        """Send a message to an agent's Discord channel."""
        # Determine channel ID if orchestrator provides it
        channel_id = None
        if getattr(self, "orchestrator", None) and hasattr(
            self.orchestrator, "agent_channel_ids"
        ):
            channel_id = self.orchestrator.agent_channel_ids.get(agent)
        # Attempt to get channel regardless of channel_id being None
        channel = self.get_channel(channel_id)
        if channel:
            try:
                # Properly await the async call to send
                await channel.send(payload)
            except Exception as e:
                logger.error(f"Failed to send message to {agent}'s channel: {e}")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

        # Announce in agent-feed or general channel with agent list
        emoji_map = {
            "architect_agent": "🏗",
            "metrics_agent": "📊",
            "ux_designer_agent": "🎨",
            "therapist_agent": "🗣",
            "ping_agent": "📶",
            "echo_agent": "🔁",
            "healthcheck_agent": "✅",
        }

        agent_names = list(self.orchestrator._agent_objects.keys())
        agent_list = ", ".join(
            f"{emoji_map.get(name, '')} {name}" for name in agent_names
        )
        announcement = f"🟢 Legion bot is online! Available agents:\n{agent_list}"

        # Prefer agent-feed channel, fallback to general
        feed_channel_id = self.orchestrator.agent_channel_ids.get(
            "agent_feed_agent"
        ) or int(os.getenv("AGENT_FEED_CHANNEL_ID", 0))
        general_channel_id = int(os.getenv("GENERAL_CHANNEL_ID", 0))
        channel = self.get_channel(feed_channel_id) or self.get_channel(
            general_channel_id
        )

        if channel:
            await channel.send(announcement)
        else:
            logger.warning("Agent-feed/general channel not found for announcement")

        # Patch all agent objects with the live client and correct channel IDs
        for name, agent_obj in self.orchestrator._agent_objects.items():
            if hasattr(agent_obj, "client"):
                agent_obj.client = self
            if hasattr(agent_obj, "channel_id"):
                agent_obj.channel_id = self.orchestrator.agent_channel_ids.get(name, 0)

        # Schedule maintenance tasks
        self.loop.create_task(self._schedule_maintenance())

    async def _schedule_maintenance(self):
        """Schedule periodic maintenance tasks."""
        try:
            # Initial self-assess after 10 minutes
            await asyncio.sleep(600)
            if not self._shutdown_event.is_set():
                await run_self_assess_all(self.orchestrator)

            # Hourly tasks
            while not self._shutdown_event.is_set():
                await asyncio.sleep(3600)
                await run_self_assess_all(self.orchestrator)
                processed_message_ids.clear()

        except asyncio.CancelledError:
            logger.info("Maintenance tasks cancelled")
        except Exception as e:
            logger.error(f"Error in maintenance tasks: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Only handle each message once
        if message.id in processed_message_ids:
            return
        processed_message_ids.add(message.id)

        # Enforce one-at-a-time handling
        async with message_processing_lock:
            try:
                # Map channel name to agent name (1:1)
                channel_to_agent = {
                    v: k for k, v in self.orchestrator.agent_channel_ids.items()
                }
                agent_name = channel_to_agent.get(message.channel.name)

                if not agent_name:
                    return  # Not an agent channel

                response = await self.orchestrator.dispatch_message(
                    agent_name=agent_name,
                    content=message.content,
                    author=message.author.name,
                    timestamp=message.created_at.isoformat(),
                )

                if response:
                    await message.channel.send(response)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await message.channel.send("⚠️ Error processing message.")

async def run_self_assess_all(orchestrator):
    logger.info("Self-assessment round starting...")
    for agent in orchestrator.agents.values():
        try:
            await agent.self_assess()
        except Exception as e:
            logger.error(f"Self-assess failed for {agent.name}: {e}")


async def main():
    """Main entry point for the Discord bot."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set in environment or .env file")
        sys.exit(1)

    try:
        # Try to create new orchestrator
        orchestrator = Orchestrator()
        bot = LegionBot(orchestrator=orchestrator)

        # Run the bot
        async with bot:
            await bot.start(token)

    except ProcessRunningError as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


# Export a LegionBot instance for test imports
bot = LegionBot()

if __name__ == "__main__":
    asyncio.run(main())
