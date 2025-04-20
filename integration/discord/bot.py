"""Discord bot stub for Legion integration."""

import discord
import asyncio
import logging
import os
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands

from legion.orchestrator import Orchestrator

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
        async for msg in history_obj.history(limit=limit):
            messages.append(msg)
        return list(reversed(messages))
    except Exception as e:
        logging.warning(f"[fetch_thread_history] Failed to fetch thread history: {e}")
        return []


class LegionBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix="!", intents=intents, *args, **kwargs)
        self.agent_tasks = []
        # self.orchestrator will be set in setup_hook

    async def setup_hook(self):
        # Instantiate orchestrator before adding cogs
        self.orchestrator = Orchestrator()
        # override the placeholder with a real Discord sender
        self.orchestrator._post_agent_message = lambda agent, payload: \
            self.get_channel(self.orchestrator.agent_channel_ids[agent]).send(payload)
        from integration.discord.cogs.orchestrator import OrchestratorCog
        await self.add_cog(OrchestratorCog(self, self.orchestrator))
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        logging.info("ready")
        # Announce in agent-feed or general channel with agent list
        emoji_map = {
            "architect_agent": "🏗️",
            "metrics_agent": "📊",
            "ux_designer_agent": "🎨",
            "therapist_agent": "🗣️",
            "ping_agent": "📶",
            "echo_agent": "🔁",
            "healthcheck_agent": "✅",
        }
        agent_names = list(self.orchestrator._agent_objects.keys())
        agent_list = ", ".join(f"{emoji_map.get(name, '')} {name}" for name in agent_names)
        announcement = f"🟢 Legion bot is online! Available agents:\n{agent_list}"
        # Prefer agent-feed channel, fallback to general
        feed_channel_id = self.orchestrator.agent_channel_ids.get("agent_feed_agent") or int(os.getenv("AGENT_FEED_CHANNEL_ID", 0))
        general_channel_id = int(os.getenv("GENERAL_CHANNEL_ID", 0))
        channel = self.get_channel(feed_channel_id) or self.get_channel(general_channel_id)
        if channel:
            await channel.send(announcement)
        else:
            logging.warning(f"Agent-feed/general channel not found for announcement.")
        # Patch all agent objects with the live client and correct channel IDs
        for name, agent_obj in self.orchestrator._agent_objects.items():
            if hasattr(agent_obj, "client"):
                agent_obj.client = self
            if hasattr(agent_obj, "channel_id"):
                agent_obj.channel_id = self.orchestrator.agent_channel_ids.get(name, 0)
        # Schedule a one-off self-assess for all agents after 10 minutes
        async def delayed_self_assess():
            await asyncio.sleep(600)
            await run_self_assess_all(self.orchestrator)
        asyncio.create_task(delayed_self_assess())

        # Schedule a repeating hourly self-assess for all agents
        async def hourly_loop():
            while True:
                await asyncio.sleep(3600)
                await run_self_assess_all(self.orchestrator)
        asyncio.create_task(hourly_loop())

        # Schedule a repeating hourly prune of processed_message_ids
        async def prune_processed_message_ids():
            while True:
                await asyncio.sleep(3600)
                processed_message_ids.clear()
        asyncio.create_task(prune_processed_message_ids())

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Only handle each message once
        if message.id in processed_message_ids:
            return
        processed_message_ids.add(message.id)

        # Enforce one-at-a-time handling
        async with message_processing_lock:
            # Map channel name to agent name (1:1)
            channel_to_agent = {v: k for k, v in self.orchestrator.agent_channel_ids.items()}
            agent_name = channel_to_agent.get(message.channel.name)
            if not agent_name:
                return  # Not an agent channel
            response = await self.orchestrator.dispatch_to_agent(
                agent_name=agent_name,
                message=message
            )
            if response:
                await message.channel.send(response)

# New helper for self-assessment rounds
async def run_self_assess_all(orchestrator):
    logger.info("Self-assessment round starting...")
    for agent in orchestrator.agents.values():
        try:
            await agent.self_assess()
        except Exception as e:
            logger.error(f"Self-assess failed for {agent.name}: {e}")

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("[FATAL] DISCORD_TOKEN not set in environment or .env file.")
        exit(1)
    bot = LegionBot()
    await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
