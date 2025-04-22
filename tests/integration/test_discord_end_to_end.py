from unittest.mock import MagicMock

import discord
import pytest

from legion.discord.commands import LegionCommandCog
from legion.orchestrator import Orchestrator


class DummyChannel:
    def __init__(self):
        self.sent = []

    async def send(self, msg):
        self.sent.append(msg)


class DummyContext:
    def __init__(self, channel):
        self.channel = channel
        self.sent = []
        self.author = MagicMock(display_name="tester")

    async def send(self, *args, **kwargs):
        # Match the structure used in the unit tests
        self.sent.append({"args": args, "kwargs": kwargs})


@pytest.mark.asyncio
async def test_config_command_end_to_end(monkeypatch):
    orch = MagicMock(spec=Orchestrator)
    logs_channel = DummyChannel()
    invoking_channel = DummyChannel()
    # Patch orchestrator to post to agent_logs
    orch.agent_channel_ids = {"agent_logs": 42, "config_updates": 123}
    orch.update_agent_config = MagicMock()
    # Patch bot.get_channel to return logs_channel for agent_logs
    bot = MagicMock()
    bot.get_channel = lambda cid: logs_channel if cid == 42 else invoking_channel
    cog = LegionCommandCog(bot, orch)
    ctx = DummyContext(invoking_channel)

    # Patch config_updates channel as well
    class DummyConfigChan:
        async def send(self, *args, **kwargs):
            pass

    bot.get_channel = lambda cid: (
        DummyConfigChan()
        if cid == 123
        else logs_channel if cid == 42 else invoking_channel
    )
    await cog._config_agent_impl(ctx, "echo_agent", "gpt-4", 0.7, 256)
    # Should have a reply in invoking channel
    sent = ctx.sent[0]
    embed = sent["kwargs"].get("embed")
    assert isinstance(embed, discord.Embed)
    fields = {f.name: f.value for f in embed.fields}
    assert fields["Agent"] == "echo_agent"
    assert fields["Model"] == "gpt-4"
    assert fields["Temperature"] == "0.7"
    assert fields["Max Tokens"] == "256"
    # (Stub) Would post to logs_channel in real implementation
