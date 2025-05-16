from unittest.mock import AsyncMock

import discord
import pytest

from integration.discord.cogs.ux_feed import (
    MessageType,
    render_error,
    render_info,
    render_message,
    render_success,
    render_warning,
)


@pytest.fixture
def mock_channel():
    channel = AsyncMock()
    channel.send = AsyncMock()
    return channel


def test_message_type_enum():
    """Test MessageType enum values."""
    assert MessageType.INFO.value == "info"
    assert MessageType.WARNING.value == "warning"
    assert MessageType.ERROR.value == "error"
    assert MessageType.SUCCESS.value == "success"


@pytest.mark.asyncio
async def test_render_info():
    """Test info message rendering."""
    message = "Test info message"
    embed = render_info(message)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "\u2139\ufe0f Info"
    assert embed.description == message
    assert embed.color == discord.Color.blue()


@pytest.mark.asyncio
async def test_render_warning():
    """Test warning message rendering."""
    message = "Test warning message"
    embed = render_warning(message)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "⚠️ Warning"
    assert embed.description == message
    assert embed.color == discord.Color.yellow()


@pytest.mark.asyncio
async def test_render_error():
    """Test error message rendering."""
    message = "Test error message"
    embed = render_error(message)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "❌ Error"
    assert embed.description == message
    assert embed.color == discord.Color.red()


@pytest.mark.asyncio
async def test_render_success():
    """Test success message rendering."""
    message = "Test success message"
    embed = render_success(message)

    assert isinstance(embed, discord.Embed)
    assert embed.title == "✅ Success"
    assert embed.description == message
    assert embed.color == discord.Color.green()


@pytest.mark.asyncio
async def test_render_message_all_types():
    """Test render_message with all message types."""
    test_cases = [
        (MessageType.INFO, render_info),
        (MessageType.WARNING, render_warning),
        (MessageType.ERROR, render_error),
        (MessageType.SUCCESS, render_success),
    ]

    message = "Test message"
    for msg_type, render_func in test_cases:
        embed = render_message(msg_type, message)
        expected_embed = render_func(message)

        assert isinstance(embed, discord.Embed)
        assert embed.title == expected_embed.title
        assert embed.description == expected_embed.description
        assert embed.color == expected_embed.color


@pytest.mark.asyncio
async def test_render_message_invalid_type():
    """Test render_message with invalid message type."""
    with pytest.raises(ValueError):
        render_message("invalid_type", "Test message")
