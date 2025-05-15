import asyncio
from unittest.mock import AsyncMock, patch
import discord
from integration.discord.bot import LegionBot

async def test_send_agent_message():
    bot = LegionBot()
    bot.get_channel = AsyncMock()
    channel = AsyncMock()
    bot.get_channel.return_value = channel
    await bot._send_agent_message("test_agent", "Test message")
    channel.send.assert_called_with("Test message")
