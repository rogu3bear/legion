"""
Discord bot integration for Legion.
"""
from dotenv import load_dotenv
import os, logging, discord, yaml, sys
from discord.ext import commands
from discord import app_commands, Interaction
from src.orchestrator import Orchestrator
from src.ux_feed import render_feed_item
import functools

load_dotenv(dotenv_path=".env/.env")
token = os.getenv("DISCORD_TOKEN")
channel_id = os.getenv("DISCORD_CHANNEL_ID")
if not token or not channel_id:
    # Fallback to YAML config
    try:
        with open("config/discord_bot_config.yaml", "r") as f:
            config = yaml.safe_load(f)
            token = token or config.get("token")
            channel_id = channel_id or config.get("channel_id")
    except Exception as e:
        print(f"Error loading Discord config: {e}")
        sys.exit(1)
if not token or not channel_id:
    print("Discord token or channel_id not set in environment or config/discord_bot_config.yaml. Exiting.")
    sys.exit(1)
channel_id = int(channel_id)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

class LegionBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        # Wrap the async post_agent_message for orchestrator
        def post_agent_message_sync(agent_name, embed):
            import asyncio
            asyncio.create_task(post_agent_message(agent_name, embed))
        self.orch = Orchestrator(post_agent_message=post_agent_message_sync)
        self.channel_id = channel_id
        self.agent_channels = self._resolve_agent_channels()

    def _resolve_agent_channels(self):
        # Map agent names to Discord channel objects (by name)
        mapping = {}
        for name, ch_name in self.orch.agent_registry.items():
            mapping[name] = None  # Will resolve on_ready
        return mapping

    async def setup_hook(self):
        guild = discord.Object(id=1362899585726418988)
        await self.tree.sync(guild=guild)
        print("Synced slash commands to guild:", 1362899585726418988)

bot = LegionBot()

@bot.event
async def on_ready():
    # Validate channels and permissions
    ok, summary = await validate_channels(bot)
    if not ok:
        print("FATAL: Channel validation failed. See logs for details.")
        import sys
        sys.exit(1)
    # Send a test message to the main channel
    main_channel = bot.get_channel(bot.channel_id)
    if main_channel:
        await main_channel.send("Legion bot is online!")
    # Resolve agent channels by name
    for agent, ch_name in bot.orch.agent_registry.items():
        for channel in bot.get_all_channels():
            if channel.name == bot.orch.get_agent_channel(agent):
                bot.agent_channels[agent] = channel
    print(f"Logged in as {bot.user}")
    # Post initial status and self-assessment for each agent
    for agent in bot.orch.agent_registry:
        ch = bot.agent_channels.get(agent)
        if ch:
            summary = bot.orch.self_assess(agent)
            await ch.send(embed=render_feed_item(agent, summary))
    # Start periodic self-assessment loop
    import asyncio
    asyncio.create_task(bot.orch.periodic_assessments())

@bot.tree.command(name="list_agents", description="Show available personas")
async def list_agents(interaction: Interaction):
    agents = list(bot.orch.agent_registry.keys())
    embed = discord.Embed(title="Available Agents", description="\n".join(agents))
    await interaction.response.send_message(embed=embed)
    logger.info(f"/list_agents executed by {interaction.user}")

@bot.tree.command(name="ask", description="Ask a single agent")
@app_commands.describe(agent_name="Agent", prompt="Your prompt")
async def ask(interaction: Interaction, agent_name: str, prompt: str):
    if agent_name not in bot.orch.agent_registry:
        await interaction.response.send_message(f"Unknown agent `{agent_name}`", ephemeral=True)
        logger.info(f"/ask failed for agent '{agent_name}' by {interaction.user}")
        return
    reply = bot.orch.ask(agent_name, prompt)
    ch = bot.agent_channels.get(agent_name)
    if ch:
        await ch.send(embed=render_feed_item(agent_name, reply))
    await interaction.response.send_message(embed=render_feed_item(agent_name, reply))
    logger.info(f"/ask executed for agent '{agent_name}' by {interaction.user}")

@bot.tree.command(name="broadcast", description="Ask all agents")
@app_commands.describe(prompt="Your prompt")
async def broadcast(interaction: Interaction, prompt: str):
    responses = bot.orch.broadcast(prompt)
    for resp in responses:
        ch = bot.agent_channels.get(resp["agent"])
        if ch:
            await ch.send(embed=render_feed_item(resp["agent"], resp["response"]))
        await interaction.channel.send(embed=render_feed_item(resp["agent"], resp["response"]))
    logger.info(f"/broadcast executed by {interaction.user}")

@bot.tree.command(name="comment", description="Comment on another agent's post")
@app_commands.describe(agent_name="Your agent", target_agent="Target agent", comment="Comment text")
async def comment(interaction: Interaction, agent_name: str, target_agent: str, comment: str):
    bot.orch.comment_on_post(agent_name, target_agent, comment)
    ch = bot.agent_channels.get(target_agent)
    if ch:
        await ch.send(f"{agent_name} commented: {comment}")
    await interaction.response.send_message(f"Comment posted to {target_agent}")
    logger.info(f"/comment by {agent_name} on {target_agent} by {interaction.user}")

@bot.tree.command(name="react", description="React to another agent's post")
@app_commands.describe(agent_name="Your agent", target_agent="Target agent", emoji="Emoji")
async def react(interaction: Interaction, agent_name: str, target_agent: str, emoji: str):
    bot.orch.react_to_post(agent_name, target_agent, emoji)
    ch = bot.agent_channels.get(target_agent)
    if ch:
        async for msg in ch.history(limit=10):
            await msg.add_reaction(emoji)
            break
    await interaction.response.send_message(f"Reacted to {target_agent}'s latest post with {emoji}")
    logger.info(f"/react by {agent_name} on {target_agent} by {interaction.user}")

@bot.tree.command(name="request_assistance", description="Request help from therapist agent")
@app_commands.describe(agent_name="Your agent", issue="Describe the issue")
async def request_assistance(interaction: Interaction, agent_name: str, issue: str):
    bot.orch.request_assistance(agent_name, issue)
    ch = bot.agent_channels.get("therapist_agent")
    if ch:
        await ch.send(f"{agent_name} requests assistance: {issue}")
    await interaction.response.send_message(f"Assistance request sent to therapist_agent")
    logger.info(f"/request_assistance by {agent_name} by {interaction.user}")

@bot.tree.command(name="assess_all", description="Trigger self-assessment for all agents")
async def assess_all(interaction: Interaction):
    results = bot.orch.assess_all_agents()
    summary_lines = []
    for agent, assessment in results.items():
        ch = bot.agent_channels.get(agent)
        if ch:
            await ch.send(embed=render_feed_item(agent, assessment))
        summary_lines.append(f"**{agent}:** {assessment[:100]}{'...' if len(assessment) > 100 else ''}")
    summary = "\n".join(summary_lines)
    await interaction.response.send_message(f"Self-assessments triggered for all agents.\n\n{summary}")
    logger.info(f"/assess_all executed by {interaction.user}")

@bot.tree.command(name="status", description="Show Legion system health and channel status")
async def status(interaction: Interaction):
    ok, summary = await validate_channels(bot)
    # Check agent instantiation
    agent_alive = all(name in bot.orch._agent_objects for name in bot.orch.agent_registry)
    agent_msg = "✅ All agents instantiated" if agent_alive else "❌ Agent instantiation error"
    # Check memory health
    try:
        mem_ok = all(bot.orch.memory[name] for name in bot.orch.agent_registry)
        mem_msg = f"✅ Memory OK for {len(bot.orch.memory)} agents" if mem_ok else "❌ Memory error"
    except Exception as e:
        mem_msg = f"❌ Memory error: {e}"
    embed = discord.Embed(title="Legion System Status")
    embed.add_field(name="Channel Validation", value=summary, inline=False)
    embed.add_field(name="Agent Instantiation", value=agent_msg, inline=False)
    embed.add_field(name="Memory Health", value=mem_msg, inline=False)
    await interaction.response.send_message(embed=embed)

async def post_agent_message(agent_name: str, embed):
    ch = bot.agent_channels.get(agent_name)
    if ch:
        try:
            await ch.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to post message to {agent_name} channel: {e}")
    else:
        logger.error(f"No Discord channel found for agent {agent_name}")

async def validate_channels(bot):
    """Check that all agent channels exist and bot has required permissions."""
    results = {}
    for agent, channel_id in bot.orch.agent_channel_ids.items():
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                channel = await bot.fetch_channel(int(channel_id))
            perms = channel.permissions_for(channel.guild.me)
            if not (perms.send_messages and perms.embed_links):
                results[agent] = f"❌ Missing permissions in <#{channel_id}>"
            else:
                results[agent] = f"✅ Channel <#{channel_id}> OK"
        except Exception as e:
            results[agent] = f"❌ Channel <#{channel_id}> error: {e}"
    all_ok = all(v.startswith('✅') for v in results.values())
    summary = "\n".join(f"{agent}: {msg}" for agent, msg in results.items())
    if all_ok:
        bot.logger.info("✅ Channel validation passed")
    else:
        bot.logger.error(f"Channel validation failed:\n{summary}")
    return all_ok, summary

if __name__ == "__main__":
    print("Registered slash commands:", [cmd.name for cmd in bot.tree.get_commands()])
    bot.run(token)
