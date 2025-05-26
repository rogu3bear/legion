from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from discord.ext import commands

from legion.discord.commands import LegionCommandCog


@pytest.fixture
async def bot_and_cog(monkeypatch):
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    orchestrator = MagicMock()
    cog = LegionCommandCog(bot, orchestrator)
    return bot, cog, orchestrator


class MockAuthor:
    def __init__(self, name="TestUser", id=123):
        self.name = name
        self.id = id
        self.display_name = name


class MockCtx:
    def __init__(self):
        self.sent_messages = []
        self.author = MockAuthor()
        self.channel = self
        self.guild = None
        self._raw_send_content = None  # To capture raw string send

    async def send(self, content=None, embed=None):
        if content and not embed:  # Capturing raw string send for the exception case
            self._raw_send_content = content
        self.sent_messages.append({"content": content, "embed": embed})
        mock_message = MagicMock(spec=discord.Message)
        mock_message.edit = AsyncMock()
        return mock_message


@pytest.mark.asyncio
async def test_create_task_success_direct_call(bot_and_cog):
    bot, cog, orchestrator = bot_and_cog
    orchestrator.dispatch_command.return_value = {
        "status": "success",
        "task_id": "abc123",
    }

    ctx = MockCtx()
    # Directly call the command's callback to bypass command dispatch
    await cog.create_task.callback(cog, ctx, "executor", "deploy patch", 0.9)

    assert ctx.sent_messages, "No message sent on success"
    response = ctx.sent_messages[0]
    embed = response["embed"]
    assert embed is not None, "Embed not sent on success"
    assert embed.title == "Task Created"  # Corrected title

    expected_fields = {
        "Task ID": "abc123",
        "Agent": "executor",
        "Directive": "deploy patch",
        "Confidence": "0.9",
    }
    present_fields = {f.name: f.value for f in embed.fields}
    assert (
        present_fields == expected_fields
    ), f"Embed fields mismatch. Got: {present_fields}, Expected: {expected_fields}"

    orchestrator.dispatch_command.assert_called_once_with(
        {
            "action": "create_task",
            "payload": {
                "agent": "executor",
                "directive": "deploy patch",
                "confidence": 0.9,
            },
        }
    )


@pytest.mark.asyncio
async def test_create_task_failure_from_orchestrator_direct_call(bot_and_cog):
    bot, cog, orchestrator = bot_and_cog
    orchestrator.dispatch_command.return_value = {
        "status": "error",
        "detail": "Middleware rejection detail",
    }

    ctx = MockCtx()
    # Direct callback for failure case
    await cog.create_task.callback(cog, ctx, "executor", "invalid directive", 0.95)

    assert ctx.sent_messages, "No message sent on orchestrator failure"
    response = ctx.sent_messages[0]
    embed = response["embed"]
    assert embed is not None, "Embed not sent on orchestrator failure"
    assert embed.title == "Task Creation Failed"  # Corrected title
    assert embed.description == "Middleware rejection detail"


@pytest.mark.asyncio
async def test_create_task_other_exception_direct_call(bot_and_cog):
    bot, cog, orchestrator = bot_and_cog
    orchestrator.dispatch_command.side_effect = Exception("Some other unexpected error")

    ctx = MockCtx()
    # Direct callback for unexpected exception
    await cog.create_task.callback(cog, ctx, "executor", "some directive", 0.9)

    assert ctx.sent_messages, "No message sent on other exception"
    assert ctx._raw_send_content == "Error creating task: Some other unexpected error"
    assert ctx.sent_messages[0]["embed"] is None  # Ensure no embed was sent
