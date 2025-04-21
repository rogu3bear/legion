import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
import pytest_asyncio

from integration.discord.bot import bot as legion_bot
from legion.orchestrator import Orchestrator

# --- Fixtures and Helpers ---


@pytest_asyncio.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest_asyncio.fixture
def bot(monkeypatch):
    # Patch environment and channel IDs to match dev scaffold
    os.environ["DISCORD_TOKEN"] = "test-token"
    # Load channel IDs from discord_channels.yaml if present
    # (Stub: in real test, parse YAML and set env vars)
    # monkeypatch.setenv(...)
    # Patch discord.Client.run to not actually connect
    with patch.object(discord.Client, "run", lambda self, *a, **k: None):
        yield legion_bot


@pytest_asyncio.fixture
def guild():
    # Return a MagicMock guild/server stub
    g = MagicMock(spec=discord.Guild)
    g.id = 123456789
    g.name = "TestGuild"
    return g


async def fetch_last_message(channel):
    # Helper to get last message from a channel (stub)
    if hasattr(channel, "history"):
        messages = [m async for m in channel.history(limit=1)]
        return messages[0] if messages else None
    return None


# --- Integration Tests ---


@pytest.mark.asyncio
async def test_config_agent_slash_command(bot, guild):
    # Simulate /config agent echo_agent gpt-4 0.7 256
    orch = Orchestrator()
    orch.agent_channel_ids = {"agent_logs": 42, "config_updates": 123}
    orch.update_agent_config = MagicMock()
    # Patch bot.get_channel to return mocks for config_updates and agent_logs
    config_chan = MagicMock()
    config_chan.send = AsyncMock()
    logs_chan = MagicMock()
    invoking_channel = MagicMock()
    bot.get_channel = lambda cid: (
        config_chan if cid == 123 else logs_chan if cid == 42 else invoking_channel
    )

    # Patch ctx to use AsyncMock for send
    class DummyCtx:
        def __init__(self):
            self.author = MagicMock(display_name="tester")
            self.send = AsyncMock()

    ctx = DummyCtx()
    # Get LegionCommandCog instance
    from legion.discord.commands import LegionCommandCog

    cog = LegionCommandCog(bot, orch)
    await cog._config_agent_impl(ctx, "echo_agent", "gpt-4", 0.7, 256)
    # Find the call to ctx.send with an embed
    embed = None
    for call in ctx.send.call_args_list:
        if "embed" in call.kwargs and isinstance(call.kwargs["embed"], discord.Embed):
            embed = call.kwargs["embed"]
            break
    assert embed is not None
    fields = {f.name: f.value for f in embed.fields}
    assert fields["Agent"] == "echo_agent"
    assert fields["Model"] == "gpt-4"
    assert fields["Temperature"] == "0.7"
    assert fields["Max Tokens"] == "256"
    # Assert config-update embed sent to config_updates channel
    assert config_chan.send.call_count == 1
    config_embed = config_chan.send.call_args.kwargs.get("embed")
    assert isinstance(config_embed, discord.Embed)
    config_fields = {f.name: f.value for f in config_embed.fields}
    assert config_fields == fields


@pytest.mark.asyncio
async def test_state_query_slash_command(bot, guild):
    # Simulate /state query therapist.threshold
    orch = Orchestrator()
    orch.get_state_key = MagicMock(return_value="42")

    # Patch ctx to use AsyncMock for send
    class DummyCtx:
        def __init__(self):
            self.author = MagicMock(display_name="tester")
            self.send = AsyncMock()

    ctx = DummyCtx()
    from legion.discord.commands import LegionCommandCog

    cog = LegionCommandCog(bot, orch)
    await cog._state_query_impl(ctx, "therapist.threshold")
    # Find the call to ctx.send with an embed
    embed = None
    for call in ctx.send.call_args_list:
        if "embed" in call.kwargs and isinstance(call.kwargs["embed"], discord.Embed):
            embed = call.kwargs["embed"]
            break
    assert embed is not None, "Expected an embed in one of the ctx.send calls"
    assert embed.title == "State Query: therapist.threshold"
    assert embed.description == "42"


@pytest.mark.asyncio
async def test_feedback_slash_command(bot, guild):
    # Simulate /feedback 1234567890 bad
    orch = Orchestrator()
    orch.agent_channel_ids = {"agent_feedback": 456, "agent_logs": 42}
    orch.submit_feedback = MagicMock()
    # Patch bot.get_channel to return mocks for agent_feedback and agent_logs
    feedback_chan = MagicMock()
    feedback_chan.send = AsyncMock()
    logs_chan = MagicMock()
    invoking_channel = MagicMock()
    bot.get_channel = lambda cid: (
        feedback_chan if cid == 456 else logs_chan if cid == 42 else invoking_channel
    )

    # Patch ctx to use AsyncMock for send
    class DummyCtx:
        def __init__(self):
            self.author = MagicMock(display_name="tester")
            self.send = AsyncMock()

    ctx = DummyCtx()
    from legion.discord.commands import LegionCommandCog

    cog = LegionCommandCog(bot, orch)
    await cog._feedback_impl(ctx, "1234567890", "bad")
    # Find the call to ctx.send with an embed
    embed = None
    for call in ctx.send.call_args_list:
        if "embed" in call.kwargs and isinstance(call.kwargs["embed"], discord.Embed):
            embed = call.kwargs["embed"]
            break
    assert embed is not None, "Expected an embed in one of the ctx.send calls"
    fields = {f.name: f.value for f in embed.fields}
    assert fields["Message ID"] == "1234567890"
    assert fields["Rating"] == "bad"
    # Assert feedback embed sent to agent_feedback channel
    assert feedback_chan.send.call_count == 1
    feedback_embed = feedback_chan.send.call_args.kwargs.get("embed")
    assert isinstance(feedback_embed, discord.Embed)
    feedback_fields = {f.name: f.value for f in feedback_embed.fields}
    assert feedback_fields == fields


@pytest.mark.asyncio
async def test_alert_subscribe_and_alert_flow(bot, guild):
    # Simulate /alert subscribe and orchestrator alert
    orch = Orchestrator()
    orch.agent_channel_ids = {"agent_logs": 42}
    orch.add_alert_subscriber = MagicMock()

    # Patch ctx to use AsyncMock for send and author.send
    class DummyCtx:
        def __init__(self):
            self.author = MagicMock(display_name="tester", id=123)
            self.author.send = AsyncMock()
            self.send = AsyncMock()

    ctx = DummyCtx()
    from legion.discord.commands import LegionCommandCog

    cog = LegionCommandCog(bot, orch)
    await cog._alert_subscribe_impl(ctx)
    # Assert DM sent to user
    assert ctx.author.send.call_count == 1
    dm_msg = ctx.author.send.call_args.args[0]
    assert "subscribed to Legion critical alerts" in dm_msg
    # Assert confirmation sent in channel
    found = False
    for call in ctx.send.call_args_list:
        if "subscribed to alerts" in (call.args[0] if call.args else ""):
            found = True
            break
    assert found, "Expected confirmation message in ctx.send calls"


@pytest.mark.asyncio
async def test_message_event_flow(bot, guild):
    # Simulate invalid message flow
    orch = Orchestrator()
    orch.agent_channel_ids = {"agent_logs": 42}
    # Patch agent with validate_request returning False and fallback_response
    agent = MagicMock()
    agent.validate_request = MagicMock(return_value=False)
    agent.fallback_response = MagicMock(return_value="Fallback reply")
    agent.post_to_discord = AsyncMock()
    orch.agents = {"echo_agent": agent}
    orch.agent_configs = {"echo_agent": {}}
    orch._agent_objects = orch.agents
    # Patch bot.get_channel to return logs_chan for agent_logs
    logs_chan = MagicMock()
    logs_chan.send = AsyncMock()
    bot.get_channel = lambda cid: logs_chan if cid == 42 else None
    # Patch orchestrator.state.log_task to avoid side effects
    orch.state.log_task = MagicMock()
    # Simulate invalid message dispatch
    await orch.dispatch_message("echo_agent", "invalid content", author="tester")
    # Assert fallback_response was called
    assert agent.fallback_response.called
    # Simulate valid message flow
    agent.validate_request = MagicMock(return_value=True)
    agent.handle_message = AsyncMock(return_value="Valid reply")
    await orch.dispatch_message("echo_agent", "valid content", author="tester")
    assert agent.handle_message.called
    reply = await agent.handle_message("valid content", author="tester", timestamp=None)
    assert reply == "Valid reply"


@pytest.mark.asyncio
async def test_error_handling_invalid_args(bot, guild):
    # Simulate a command with missing/invalid arguments and assert error message
    orch = Orchestrator()

    # Patch ctx to use AsyncMock for send
    class DummyCtx:
        def __init__(self):
            self.author = MagicMock(display_name="tester")
            self.send = AsyncMock()

    ctx = DummyCtx()
    from legion.discord.commands import LegionCommandCog

    cog = LegionCommandCog(bot, orch)
    # Call _config_agent_impl with missing/invalid args to trigger error
    await cog._config_agent_impl(ctx, None, None, None, None)
    # Assert error message sent
    found = False
    for call in ctx.send.call_args_list:
        if "Error updating config" in (call.args[0] if call.args else ""):
            found = True
            break
    assert found, "Expected error message in ctx.send calls"


# --- CI Integration ---
# This file will be picked up by pytest and GitHub Actions as long as it is in tests/discord/
