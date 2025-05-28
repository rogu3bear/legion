import datetime
from datetime import timezone
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from integration.discord.cogs.orchestrator import OrchestratorCog
from legion.orchestrator import Orchestrator


# Fixture for a mocked bot instance
@pytest.fixture
def mock_bot():
    bot = MagicMock(spec=discord.ext.commands.Bot)
    bot.loop = MagicMock()
    bot.orchestrator = MagicMock(spec=Orchestrator)
    bot.orchestrator.agent_channel_ids = {"TestAgent": 123, "OtherAgent": 456}
    bot.orchestrator._agent_objects = {
        "TestAgent": MagicMock()
        "OtherAgent": MagicMock()
    }
    bot.add_cog = AsyncMock()  # Mock add_cog as it's called during setup
    return bot


# Fixture for the OrchestratorCog instance
@pytest.fixture
def orchestrator_cog(mock_bot):
    return OrchestratorCog(mock_bot, mock_bot.orchestrator)


# Fixture for a mocked interaction
@pytest.fixture
def mock_interaction():
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.response = AsyncMock(spec=discord.InteractionResponse)
    interaction.followup = AsyncMock(spec=discord.Webhook)
    interaction.user = MagicMock(spec=discord.User)
    interaction.user.name = "TestUser"
    interaction.user.id = 987
    interaction.channel = MagicMock(spec=discord.TextChannel)
    interaction.channel.id = 111
    interaction.client = MagicMock()  # Mock the client attribute
    interaction.client.orchestrator = MagicMock(
        spec=Orchestrator
    )  # Ensure client has orchestrator
    interaction.client.orchestrator.agent_channel_ids = {
        "TestAgent": 123
        "OtherAgent": 456
    }
    return interaction


@pytest.mark.asyncio
async def test_reload_configs_command(orchestrator_cog, mock_interaction):
    """Test the /reload_configs slash command."""
    await orchestrator_cog.reload_configs(mock_interaction)

    # Assert orchestrator method was called
    orchestrator_cog.orchestrator.reload_agent_configs.assert_called_once()

    # Assert response was sent
    mock_interaction.response.send_message.assert_called_once_with(
        "Agent configurations reloaded.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_ask_command_success(orchestrator_cog, mock_interaction):
    """Test the /ask slash command with a valid agent."""
    agent_name = "TestAgent"
    question = "What is the status?"
    expected_reply = "The status is green."

    # Mock the orchestrator's dispatch_message to return a reply
    mock_interaction.client.orchestrator.dispatch_message = AsyncMock(
        return_value=expected_reply
    )

    await orchestrator_cog.ask(
        mock_interaction, agent_name=agent_name, question=question
    )

    # Assert dispatch_message was called correctly
    mock_interaction.client.orchestrator.dispatch_message.assert_called_once()
    call_args = mock_interaction.client.orchestrator.dispatch_message.call_args
    assert call_args.args[0] == agent_name
    assert call_args.args[1] == question
    assert call_args.kwargs["author"] == "TestUser"
    # Check timestamp is roughly correct (within a few seconds)
    timestamp_arg = datetime.datetime.fromisoformat(call_args.kwargs["timestamp"])
    assert (
        abs((datetime.datetime.now(timezone.utc) - timestamp_arg).total_seconds()) < 5
    )

    # Assert the reply was sent back
    mock_interaction.response.send_message.assert_called_once_with(expected_reply)


@pytest.mark.asyncio
async def test_ask_command_invalid_agent(orchestrator_cog, mock_interaction):
    """Test the /ask slash command with an invalid agent name."""
    agent_name = "InvalidAgent"
    question = "This should fail."

    await orchestrator_cog.ask(
        mock_interaction, agent_name=agent_name, question=question
    )

    # Assert dispatch_message was *not* called
    mock_interaction.client.orchestrator.dispatch_message.assert_not_called()

    # Assert error message was sent
    mock_interaction.response.send_message.assert_called_once()
    call_args = mock_interaction.response.send_message.call_args
    assert "Invalid agent" in call_args.args[0]
    assert "TestAgent" in call_args.args[0]
    assert "OtherAgent" in call_args.args[0]
    assert call_args.kwargs["ephemeral"] is True
