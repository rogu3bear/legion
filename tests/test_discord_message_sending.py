from unittest.mock import AsyncMock, MagicMock

from integration.discord.bot import LegionBot


async def test_send_agent_message():
    bot = LegionBot()
    bot.get_channel = MagicMock()
    channel = MagicMock()
    # Create a mock coroutine for send to be awaited
    send_coro = AsyncMock()
    channel.send = MagicMock(return_value=send_coro)
    bot.get_channel.return_value = channel

    await bot._send_agent_message("test_agent", "Test message")

    # Verify channel.send was called with the right argument
    channel.send.assert_called_once_with("Test message")
