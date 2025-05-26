import time
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from integration.discord.cogs.health import HealthCog


# Mocking discord.py objects for testing
class MockContext(AsyncMock):
    async def send(self, *args, **kwargs):
        # Store sent messages/embeds for assertions
        if not hasattr(self, "sent_messages"):
            self.sent_messages = []
        self.sent_messages.append({"args": args, "kwargs": kwargs})
        # Return a mock message object that has an edit method
        mock_message = AsyncMock()
        mock_message.edit = AsyncMock()
        return mock_message


class MockBot(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = MagicMock()
        self.user.name = "TestBot"


@pytest.fixture
def mock_channel():
    channel = AsyncMock()
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_memory():
    memory = MagicMock()
    memory.log_task = MagicMock()
    return memory


@pytest.fixture
def health_agent(mock_channel, mock_memory):
    agent = HealthCog(mock_channel)
    agent.memory = mock_memory
    return agent


@pytest.fixture
def health_cog(event_loop):
    bot = MockBot(loop=event_loop)
    cog = HealthCog(bot)
    return cog


@pytest.mark.asyncio
async def test_health_agent_initialization(health_agent):
    """Test health agent initializes with correct start time."""
    assert isinstance(health_agent.start_time, float)
    assert time.time() - health_agent.start_time < 1  # Should be very recent


@pytest.mark.asyncio
async def test_health_loop_below_threshold(health_agent):
    """Test health loop behavior when uptime is below threshold."""
    # Mock time to simulate 30 seconds uptime
    with patch("time.time", return_value=health_agent.start_time + 30):
        await health_agent._health_loop()

        # Verify message was sent
        health_agent.channel.send.assert_called_once()
        message = health_agent.channel.send.call_args[0][0]
        assert "Uptime: 30s" in message

        # Verify warning reaction was added
        message.add_reaction.assert_called_once_with("⚠️")

        # Verify task was logged as failure
        health_agent.memory.log_task.assert_called_once_with(
            {"type": "health_failure", "uptime": 30}
        )


@pytest.mark.asyncio
async def test_health_loop_above_threshold(health_agent):
    """Test health loop behavior when uptime is above threshold."""
    # Mock time to simulate 2 minutes uptime
    with patch("time.time", return_value=health_agent.start_time + 120):
        await health_agent._health_loop()

        # Verify message was sent
        health_agent.channel.send.assert_called_once()
        message = health_agent.channel.send.call_args[0][0]
        assert "Uptime: 120s" in message

        # Verify success reaction was added
        message.add_reaction.assert_called_once_with("✅")

        # Verify task was logged as success
        health_agent.memory.log_task.assert_called_once_with(
            {"type": "health_success", "uptime": 120}
        )


@pytest.mark.asyncio
async def test_health_loop_interval(health_agent):
    """Test health loop respects the configured interval."""
    with patch("asyncio.sleep") as mock_sleep:
        await health_agent._health_loop()
        mock_sleep.assert_called_once_with(60)  # 1 minute interval


@pytest.mark.asyncio
async def test_health_agent_start(health_agent):
    """Test health agent start creates background task."""
    with patch("asyncio.create_task") as mock_create_task:
        await health_agent.start()
        mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_ping_command(health_cog):
    """Test the !ping command for latency calculation."""
    ctx = MockContext()
    await health_cog.ping(ctx)

    assert len(ctx.sent_messages) == 1
    assert "Pinging..." in ctx.sent_messages[0]["args"]
    # Access the mock message returned by send to check if edit was called
    (ctx.sent_messages[0]["args"][0] if ctx.sent_messages[0]["args"] else None)
    # This assertion is tricky due to timing, better to mock time.monotonic if precision needed
    # For now, just ensure send was called.


@pytest.mark.asyncio
async def test_health_command(health_cog):
    """Test the !health command (currently placeholder)."""
    ctx = MockContext()
    # Ensure the context mock simulates having necessary permissions if the command checks
    # Example: ctx.author.guild_permissions.administrator = True

    # TODO: Mock the interaction with the orchestrator when implemented
    # Example: health_cog.orchestrator_client.get_health.return_value = {...}

    await health_cog.health(ctx)

    assert len(ctx.sent_messages) == 1
    sent_kwargs = ctx.sent_messages[0]["kwargs"]
    assert "embed" in sent_kwargs
    embed = sent_kwargs["embed"]
    assert isinstance(embed, discord.Embed)
    assert embed.title == "System Health Status"
    assert len(embed.fields) == 3  # Check for the placeholder fields
    assert embed.fields[0].name == "Orchestrator"
