from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from legion.discord.commands import LegionCommandCog
from legion.orchestrator import Orchestrator


class DummyContext:
    def __init__(self):
        self.sent = []
        self.author = MagicMock(display_name="tester", id=123)

    async def send(self, *args, **kwargs):
        # capture both positional args and keyword args (e.g. embed=Embed)
        self.sent.append({"args": args, "kwargs": kwargs})


@pytest.mark.asyncio
async def test_config_agent_parsing_and_call(monkeypatch):
    orch = MagicMock(spec=Orchestrator)
    orch.agent_channel_ids = {"config_updates": 123}
    cog = LegionCommandCog(MagicMock(), orch)
    ctx = DummyContext()
    orch.update_agent_config = MagicMock()
    called = {}

    async def fake_log(msg):
        called["log"] = msg

    monkeypatch.setattr(cog, "_log_to_agent_logs", fake_log)

    # Patch bot.get_channel to return a dummy channel with async send
    class DummyChan:
        async def send(self, *args, **kwargs):
            pass

    cog.bot.get_channel = lambda cid: DummyChan() if cid == 123 else None
    await cog._config_agent_impl(ctx, "echo_agent", "gpt-4", 0.7, 256)
    print("CTX SENT:", ctx.sent)
    sent = ctx.sent[0]
    embed = sent["kwargs"].get("embed")
    assert isinstance(embed, discord.Embed)
    fields = {f.name: f.value for f in embed.fields}
    assert fields["Agent"] == "echo_agent"
    assert fields["Model"] == "gpt-4"
    assert fields["Temperature"] == "0.7"
    assert fields["Max Tokens"] == "256"
    assert "/config" in called["log"]


@pytest.mark.asyncio
async def test_state_query_parsing_and_call(monkeypatch):
    orch = MagicMock(spec=Orchestrator)
    orch.get_state_key = MagicMock(return_value="42")
    cog = LegionCommandCog(MagicMock(), orch)
    ctx = DummyContext()
    orch.state = MagicMock()
    orch.state.get = MagicMock(return_value="42")
    called = {}

    async def fake_log(msg):
        called["log"] = msg

    monkeypatch.setattr(cog, "_log_to_agent_logs", fake_log)
    await cog._state_query_impl(ctx, "tasks")
    sent = ctx.sent[0]
    embed = sent["kwargs"].get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.title == "State Query: tasks"
    assert embed.description == "42"
    assert "/state query" in called["log"]


@pytest.mark.asyncio
async def test_feedback_parsing_and_call(monkeypatch):
    orch = MagicMock(spec=Orchestrator)
    orch.agent_channel_ids = {"agent_feedback": 456}
    cog = LegionCommandCog(MagicMock(), orch)
    ctx = DummyContext()
    orch.submit_feedback = MagicMock()
    called = {}

    async def fake_log(msg):
        called["log"] = msg

    monkeypatch.setattr(cog, "_log_to_agent_logs", fake_log)

    # Patch bot.get_channel to return a dummy channel with async send
    class DummyChan:
        async def send(self, *args, **kwargs):
            pass

    cog.bot.get_channel = lambda cid: DummyChan() if cid == 456 else None
    await cog._feedback_impl(ctx, "12345", "good")
    sent = ctx.sent[0]
    embed = sent["kwargs"].get("embed")
    assert isinstance(embed, discord.Embed)
    fields = {f.name: f.value for f in embed.fields}
    assert fields["Message ID"] == "12345"
    assert fields["Rating"] == "good"
    assert "/feedback" in called["log"]


@pytest.mark.asyncio
async def test_alert_subscribe(monkeypatch):
    orch = MagicMock(spec=Orchestrator)
    cog = LegionCommandCog(MagicMock(), orch)
    ctx = DummyContext()
    called = {}

    async def fake_log(msg):
        called["log"] = msg

    monkeypatch.setattr(cog, "_log_to_agent_logs", fake_log)
    ctx.author.send = AsyncMock()
    await cog._alert_subscribe_impl(ctx)
    sent = ctx.sent[0]
    # The confirmation string should be in the positional args
    assert any("subscribed to alerts" in str(arg) for arg in sent["args"])
    assert "subscribed to alerts" in called["log"]
