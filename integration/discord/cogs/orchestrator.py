"""Orchestrator cog stub for Discord integration."""

import discord
from discord import app_commands
from discord.ext import commands
from legion.agents.python.architect import ArchitectAgent
from legion.agents.python.metrics import MetricsAgent
from legion.agents.python.ux_designer import UxDesignerAgent
from legion.agents.python.echo import EchoAgent
from legion.agents.python.healthcheck import HealthcheckAgent
import os
import openai
import datetime


class OrchestratorCog(commands.Cog):
    def __init__(self, bot, orchestrator):
        self.bot = bot
        self.orchestrator = orchestrator

    @app_commands.command(
        name="review", description="Architect: Review the codebase structure."
    )
    async def review(self, interaction: discord.Interaction):
        agents = interaction.client.orchestrator._agent_objects
        if "architect_agent" not in agents:
            return await interaction.response.send_message("[Error: architect_agent not available]")
        await agents["architect_agent"].handle_review()
        await interaction.response.send_message("Architect review posted to channel.")

    @app_commands.command(
        name="report", description="Metrics: Post usage metrics report."
    )
    async def metrics_report(self, interaction: discord.Interaction):
        agents = interaction.client.orchestrator._agent_objects
        if "metrics_agent" not in agents:
            return await interaction.response.send_message("[Error: metrics_agent not available]")
        await agents["metrics_agent"].report()
        await interaction.response.send_message("Metrics report posted to channel.")

    @app_commands.command(
        name="llm_test", description="Test LLM endpoint connectivity."
    )
    async def llm_test(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello world"},
        ]
        try:
            loop = interaction.client.loop
            def sync_call():
                resp = openai.ChatCompletion.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    messages=messages,
                    temperature=0.3,
                    max_tokens=32,
                )
                return resp.choices[0].message.content
            response = await loop.run_in_executor(None, sync_call)
            await interaction.followup.send(f"LLM test response: {response}")
        except Exception as e:
            await interaction.followup.send(f"LLM test failed: {e}")

    @app_commands.command(
        name="critique",
        description="UX Designer: Critique and style the latest feed embeds.",
    )
    async def ux_critique(self, interaction: discord.Interaction):
        agents = interaction.client.orchestrator._agent_objects
        if "ux_designer_agent" not in agents:
            return await interaction.response.send_message("[Error: ux_designer_agent not available]")
        await agents["ux_designer_agent"].handle_critique()
        await interaction.response.send_message("UX critique posted to design channel.")

    @app_commands.command(name="echo", description="Echo a message for diagnostics.")
    @app_commands.describe(message="Message to echo back.")
    async def echo(self, interaction: discord.Interaction, message: str):
        agents = interaction.client.orchestrator._agent_objects
        if "echo_agent" not in agents:
            return await interaction.response.send_message("[Error: echo_agent not available]")
        echoed = agents["echo_agent"].handle_echo(message)
        await interaction.response.send_message(echoed)

    @app_commands.command(
        name="healthcheck", description="Run a health check on core services."
    )
    async def healthcheck(self, interaction: discord.Interaction):
        agents = interaction.client.orchestrator._agent_objects
        if "healthcheck_agent" not in agents:
            return await interaction.response.send_message("[Error: healthcheck_agent not available]")
        await agents["healthcheck_agent"].handle_healthcheck()
        await interaction.response.send_message("Health check posted to channel.")

    @app_commands.command(name="ask", description="Ask any Legion agent a question.")
    @app_commands.describe(agent_name="Which agent to ask", question="Your question")
    async def ask(self, interaction: discord.Interaction, agent_name: str, question: str):
        valid_agents = list(interaction.client.orchestrator.agent_channel_ids.keys())
        if agent_name not in valid_agents:
            await interaction.response.send_message(f"Invalid agent: {agent_name}. Valid agents: {', '.join(valid_agents)}", ephemeral=True)
            return
        print(f"[DEBUG ask] Cog orchestrator ref={self.orchestrator}, Bot orchestrator ref={interaction.client.orchestrator}")
        print(f"[DEBUG ask] Incoming agent_name={agent_name!r}, available={valid_agents}")
        context = {
            "channel_id": interaction.channel.id,
            "thread_id": getattr(interaction.channel, "id", interaction.channel.id),
            "content": question,
            "author": interaction.user.name,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
        reply = await interaction.client.orchestrator.dispatch_message(agent_name, context)
        await interaction.response.send_message(str(reply))


async def setup(bot):
    await bot.add_cog(OrchestratorCog(bot))
