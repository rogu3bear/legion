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


class OrchestratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Instantiate agents with bot and channel IDs
        general_channel_id = int(os.getenv("GENERAL_CHANNEL_ID", "0"))
        self.architect_agent = ArchitectAgent(
            "architect_agent", bot, general_channel_id
        )
        self.metrics_agent = MetricsAgent(
            "metrics_agent", bot, int(os.getenv("METRICS_CHANNEL_ID", "0"))
        )
        self.ux_designer_agent = UxDesignerAgent(
            "ux_designer_agent", bot, int(os.getenv("DESIGN_CHANNEL_ID", "0"))
        )
        self.echo_agent = EchoAgent("echo_agent", bot, general_channel_id)
        self.healthcheck_agent = HealthcheckAgent(
            "healthcheck_agent", bot, general_channel_id
        )

    @app_commands.command(
        name="review", description="Architect: Review the codebase structure."
    )
    async def review(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.architect_agent.handle_review()
        await interaction.followup.send("Architect review posted to channel.")

    @app_commands.command(
        name="report", description="Metrics: Post usage metrics report."
    )
    async def metrics_report(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.metrics_agent.report()
        await interaction.followup.send("Metrics report posted to channel.")

    @app_commands.command(
        name="llm_test", description="Test LLM endpoint connectivity."
    )
    async def llm_test(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        # Send a trivial prompt to the LLM endpoint
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
        await interaction.response.defer(thinking=True)
        await self.ux_designer_agent.handle_critique()
        await interaction.followup.send("UX critique posted to design channel.")

    @app_commands.command(name="echo", description="Echo a message for diagnostics.")
    @app_commands.describe(message="Message to echo back.")
    async def echo(self, interaction: discord.Interaction, message: str):
        echoed = self.echo_agent.handle_echo(message)
        await interaction.response.send_message(echoed)

    @app_commands.command(
        name="healthcheck", description="Run a health check on core services."
    )
    async def healthcheck(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.healthcheck_agent.handle_healthcheck()
        await interaction.followup.send("Health check posted to channel.")


async def setup(bot):
    await bot.add_cog(OrchestratorCog(bot))
