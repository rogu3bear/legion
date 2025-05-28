"""
Discord slash command handlers for Legion.
"""

import contextlib
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import discord

# Import specific discord types to ensure they're accessible
from discord import Message, Thread, User
from discord.abc import GuildChannel, Messageable, PrivateChannel
from discord.ext import commands

from legion.orchestrator import Orchestrator

if TYPE_CHECKING:
    # Precise names just for type-checking; runtime not needed.
    # from discord import Message, Thread, User # Removed as they are now imported globally by ruff
    pass


async def _safe_send(
    channel: Union[
        Messageable, GuildChannel, PrivateChannel, "Thread", Any
    ],  # Ensure Thread is quoted and Any is present
    *args: Any
    **kwargs: Any
) -> Optional["Message"]:
    """Send a message only if the channel supports .send()"""
    if isinstance(channel, Messageable):
        return await channel.send(*args, **kwargs)
    raise TypeError(f"{channel!r} is not messageable")


class LegionCommandCog(commands.Cog):
    """
    Cog for Legion slash commands: config, state, feedback, alert subscribe.
    """

    def __init__(self, bot: commands.Bot, orchestrator: Optional[Orchestrator]):
        self.bot = bot
        self.orchestrator = orchestrator

    @commands.hybrid_command(name="config", description="Update agent config.")
    async def config_agent(
        self
        ctx: commands.Context[Any]
        agent_name: str
        model: str
        temperature: float
        max_tokens: int
    ) -> None:
        """/config agent agent_name model temperature max_tokens"""
        await self._config_agent_impl(ctx, agent_name, model, temperature, max_tokens)

    async def _config_agent_impl(
        self
        ctx: commands.Context[Any]
        agent_name: str
        model: str
        temperature: float
        max_tokens: int
    ) -> None:
        """Business logic for config_agent command."""
        assert self.orchestrator is not None, "Orchestrator not initialized"
        try:
            self.orchestrator.update_agent_config(
                agent_name, model, temperature, max_tokens
            )
            embed = discord.Embed(  # Using qualified name # type: ignore[attr-defined]
                title="Agent Config Updated"
                color=discord.Color.green(),  # Using qualified name # type: ignore[attr-defined]
            )
            embed.add_field(name="Agent", value=agent_name)
            embed.add_field(name="Model", value=model)
            embed.add_field(name="Temperature", value=str(temperature))
            embed.add_field(name="Max Tokens", value=str(max_tokens))
            embed.set_footer(text="Config change applied.")
            config_chan_id = self.orchestrator.agent_channel_ids.get("config_updates")
            if config_chan_id:
                config_chan: Optional[Messageable] = self.bot.get_channel(
                    config_chan_id
                )  # type: ignore[assignment]
                if config_chan:
                    await _safe_send(config_chan, embed=embed)
            await _safe_send(ctx, embed=embed)
            await self._log_to_agent_logs(
                f"/config by {ctx.author}: {agent_name} {model} {temperature} {max_tokens}"
            )
        except Exception as e:
            await _safe_send(ctx, f"Error updating config: {e}")

    @commands.hybrid_command(name="state", description="Query orchestrator state.")
    async def state_query(self, ctx: commands.Context[Any], key: str) -> None:
        """/state query key"""
        await self._state_query_impl(ctx, key)

    async def _state_query_impl(self, ctx: commands.Context[Any], key: str) -> None:
        assert self.orchestrator is not None, "Orchestrator not initialized"
        try:
            value = self.orchestrator.get_state_key(key)
            embed = discord.Embed(  # Using qualified name # type: ignore[attr-defined]
                title=f"State Query: {key}"
                description=str(value)
                color=discord.Color.blue(),  # Using qualified name # type: ignore[attr-defined]
            )
            await _safe_send(ctx, embed=embed)
            await self._log_to_agent_logs(f"/state query by {ctx.author}: {key}")
        except Exception as e:
            await _safe_send(ctx, f"Error querying state: {e}")

    @commands.hybrid_command(
        name="feedback", description="Submit feedback on a message."
    )
    async def feedback(
        self
        ctx: commands.Context[Any]
        message_id: str
        rating: Literal["good", "borderline", "bad"]
    ) -> None:
        """/feedback message_id rating"""
        await self._feedback_impl(ctx, message_id, rating)

    async def _feedback_impl(
        self
        ctx: commands.Context[Any]
        message_id: str
        rating: Literal["good", "borderline", "bad"]
    ) -> None:
        assert self.orchestrator is not None, "Orchestrator not initialized"
        try:
            feedback_payload = {
                "type": "user_feedback"
                "message_id": message_id
                "rating": rating
                "user": str(ctx.author)
            }
            self.orchestrator.submit_feedback(feedback_payload)
            embed = discord.Embed(  # Using qualified name # type: ignore[attr-defined]
                title="Feedback Received"
                color=discord.Color.purple(),  # Using qualified name # type: ignore[attr-defined]
            )
            embed.add_field(name="Message ID", value=message_id)
            embed.add_field(name="Rating", value=rating)
            embed.set_footer(text=f"From {ctx.author.display_name}")
            fb_chan_id = self.orchestrator.agent_channel_ids.get("agent_feedback")
            if fb_chan_id:
                fb_chan: Optional[Messageable] = self.bot.get_channel(fb_chan_id)  # type: ignore[assignment]
                if fb_chan:
                    await _safe_send(fb_chan, embed=embed)
            await _safe_send(ctx, embed=embed)
            await self._log_to_agent_logs(
                f"/feedback by {ctx.author}: {message_id} {rating}"
            )
        except Exception as e:
            await _safe_send(ctx, f"Error submitting feedback: {e}")

    @commands.hybrid_command(name="alert", description="Subscribe to critical alerts.")
    async def alert_subscribe(self, ctx: commands.Context[Any]) -> None:
        """/alert subscribe"""
        await self._alert_subscribe_impl(ctx)

    async def _alert_subscribe_impl(self, ctx: commands.Context[Any]) -> None:
        assert self.orchestrator is not None, "Orchestrator not initialized"
        try:
            user_id = ctx.author.id
            self.orchestrator.add_alert_subscriber(user_id)
            if isinstance(ctx.author, Messageable):
                await _safe_send(
                    ctx.author, "You are now subscribed to Legion critical alerts."
                )
            await _safe_send(
                ctx, f"{ctx.author.display_name}, you are now subscribed to alerts."
            )
            await self._log_to_agent_logs(f"User {ctx.author} subscribed to alerts.")
        except Exception as e:
            await _safe_send(ctx, f"Error subscribing to alerts: {e}")

    async def _log_to_agent_logs(self, message: str) -> None:
        """Helper to post a log message to #agent-logs."""
        assert self.orchestrator is not None, "Orchestrator not initialized"
        logs_chan_id = self.orchestrator.agent_channel_ids.get("agent_logs")
        if logs_chan_id:
            logs_chan: Optional[Messageable] = self.bot.get_channel(logs_chan_id)  # type: ignore[assignment]
            if logs_chan:
                await _safe_send(logs_chan, f"[LOG] {message}")

    async def send_alert_to_subscribers(self, alert_message: str) -> None:
        """Send an alert DM to all subscribed users."""
        assert self.orchestrator is not None, "Orchestrator not initialized"
        for user_id in self.orchestrator.get_alert_subscribers():
            user: Optional[User] = self.bot.get_user(user_id)  # type: ignore[assignment]
            if user:  # discord.User is Messageable
                with contextlib.suppress(Exception):
                    await _safe_send(user, f"[ALERT] {alert_message}")


async def setup(bot: commands.Bot) -> None:
    orchestrator = getattr(bot, "orchestrator", None)
    await bot.add_cog(LegionCommandCog(bot, orchestrator))
