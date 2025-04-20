"""Discord bot stub for Legion integration."""

import discord
import asyncio
import logging
import os
from dotenv import load_dotenv

from legion.orchestrator import Orchestrator

# Enable logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Needed for message content access


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


class LegionBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, intents=intents, **kwargs)
        self.orchestrator = None
        self.agent_tasks = []

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        logging.info("ready")
        # Announce in general channel
        general_channel_id = int(os.getenv("GENERAL_CHANNEL_ID"))
        channel = self.get_channel(general_channel_id)
        if channel:
            await channel.send("Legion bot is online!")
        else:
            logging.warning(f"General channel {general_channel_id} not found.")
        # Instantiate orchestrator with this Discord client
        self.orchestrator = Orchestrator()
        # Patch all agent objects with the live client and correct channel IDs
        for name, agent_obj in self.orchestrator._agent_objects.items():
            if hasattr(agent_obj, "client"):
                agent_obj.client = self
            if hasattr(agent_obj, "channel_id"):
                agent_obj.channel_id = self.orchestrator.agent_channel_ids.get(name, 0)
        # Schedule self-assessment for each agent (interval = 60s for test)
        interval = 60
        for name, agent_obj in self.orchestrator._agent_objects.items():
            if hasattr(agent_obj, "self_assess"):

                async def schedule_self_assess(agent, interval):
                    # Immediate self-assess on startup
                    await agent.self_assess()
                    while True:
                        await asyncio.sleep(interval)
                        await agent.self_assess()

                task = asyncio.create_task(schedule_self_assess(agent_obj, interval))
                self.agent_tasks.append(task)

    async def on_message(self, message):
        if message.author.bot:
            return
        channel_id = message.channel.id
        if self.orchestrator and hasattr(self.orchestrator, "channel_to_agent"):
            agent = self.orchestrator.channel_to_agent.get(channel_id)
            if agent and hasattr(agent, "handle_message"):
                context = {
                    "channel_id": message.channel.id,
                    "thread_id": getattr(message, "thread", message.channel.id),
                    "content": message.content,
                    "author": message.author.name,
                    "timestamp": message.created_at,
                }
                await self.orchestrator.dispatch_message(agent.name, context)
                return
        await self.process_commands(message)


# To run the bot, you would do something like:
# import os
# bot = LegionBot()
# bot.run(os.getenv('DISCORD_TOKEN'))
