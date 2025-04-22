"""
Discord slash command handlers for Legion.
"""

from typing import Literal

import discord
from discord.ext import commands

from legion.orchestrator import Orchestrator


class LegionCommandCog(commands.Cog):
    """
    Cog for Legion slash commands: config, state, feedback, alert subscribe.
    """

    def __init__(self, bot: commands.Bot, orchestrator: Orchestrator):
        self.bot = bot
        self.orchestrator = orchestrator

    @commands.hybrid_command(name="config", description="Update agent config.")
    async def config_agent(
        self,
        ctx: commands.Context,
        agent_name: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> None:
        """/config agent agent_name model temperature max_tokens"""
        await self._config_agent_impl(ctx, agent_name, model, temperature, max_tokens)

    async def _config_agent_impl(
        self,
        ctx: commands.Context,
        agent_name: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> None:
        """Business logic for config_agent command."""
        try:
            self.orchestrator.update_agent_config(
                agent_name, model, temperature, max_tokens
            )
            embed = discord.Embed(
                title="Agent Config Updated", color=discord.Color.green()
            )
            embed.add_field(name="Agent", value=agent_name)
            embed.add_field(name="Model", value=model)
            embed.add_field(name="Temperature", value=str(temperature))
            embed.add_field(name="Max Tokens", value=str(max_tokens))
            embed.set_footer(text="Config change applied.")
            config_chan_id = self.orchestrator.agent_channel_ids.get("config_updates")
            config_chan = self.bot.get_channel(config_chan_id)
            if config_chan:
                await config_chan.send(embed=embed)
            await ctx.send(embed=embed)
            await self._log_to_agent_logs(
                f"/config by {ctx.author}: {agent_name} {model} {temperature} {max_tokens}"
            )
        except Exception as e:
            await ctx.send(f"Error updating config: {e}")

    @commands.hybrid_command(name="state", description="Query orchestrator state.")
    async def state_query(self, ctx: commands.Context, key: str) -> None:
        """/state query key"""
        await self._state_query_impl(ctx, key)

    async def _state_query_impl(self, ctx: commands.Context, key: str) -> None:
        try:
            value = self.orchestrator.get_state_key(key)
            embed = discord.Embed(
                title=f"State Query: {key}",
                description=str(value),
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)
            await self._log_to_agent_logs(f"/state query by {ctx.author}: {key}")
        except Exception as e:
            await ctx.send(f"Error querying state: {e}")

    @commands.hybrid_command(
        name="feedback", description="Submit feedback on a message."
    )
    async def feedback(
        self,
        ctx: commands.Context,
        message_id: str,
        rating: Literal["good", "borderline", "bad"],
    ) -> None:
        """/feedback message_id rating"""
        await self._feedback_impl(ctx, message_id, rating)

    async def _feedback_impl(
        self,
        ctx: commands.Context,
        message_id: str,
        rating: Literal["good", "borderline", "bad"],
    ) -> None:
        try:
            feedback = {
                "type": "user_feedback",
                "message_id": message_id,
                "rating": rating,
                "user": str(ctx.author),
            }
            self.orchestrator.submit_feedback(feedback)
            embed = discord.Embed(
                title="Feedback Received", color=discord.Color.purple()
            )
            embed.add_field(name="Message ID", value=message_id)
            embed.add_field(name="Rating", value=rating)
            embed.set_footer(text=f"From {ctx.author.display_name}")
            fb_chan_id = self.orchestrator.agent_channel_ids.get("agent_feedback")
            fb_chan = self.bot.get_channel(fb_chan_id)
            if fb_chan:
                await fb_chan.send(embed=embed)
            await ctx.send(embed=embed)
            await self._log_to_agent_logs(
                f"/feedback by {ctx.author}: {message_id} {rating}"
            )
        except Exception as e:
            await ctx.send(f"Error submitting feedback: {e}")

    @commands.hybrid_command(name="alert", description="Subscribe to critical alerts.")
    async def alert_subscribe(self, ctx: commands.Context) -> None:
        """/alert subscribe"""
        await self._alert_subscribe_impl(ctx)

    async def _alert_subscribe_impl(self, ctx: commands.Context) -> None:
        try:
            user_id = ctx.author.id
            self.orchestrator.add_alert_subscriber(user_id)
            await ctx.author.send("You are now subscribed to Legion critical alerts.")
            await ctx.send(
                f"{ctx.author.display_name}, you are now subscribed to alerts."
            )
            await self._log_to_agent_logs(f"User {ctx.author} subscribed to alerts.")
        except Exception as e:
            await ctx.send(f"Error subscribing to alerts: {e}")

    async def _log_to_agent_logs(self, message: str) -> None:
        """Helper to post a log message to #agent-logs."""
        logs_chan_id = self.orchestrator.agent_channel_ids.get("agent_logs")
        logs_chan = self.bot.get_channel(logs_chan_id)
        if logs_chan:
            await logs_chan.send(f"[LOG] {message}")

    async def send_alert_to_subscribers(self, alert_message: str) -> None:
        """Send an alert DM to all subscribed users."""
        for user_id in self.orchestrator.get_alert_subscribers():
            user = self.bot.get_user(user_id)
            if user:
                try:
                    await user.send(f"[ALERT] {alert_message}")
                except Exception:
                    pass


async def setup(bot: commands.Bot):
    orchestrator = getattr(bot, "orchestrator", None)
    await bot.add_cog(LegionCommandCog(bot, orchestrator))
