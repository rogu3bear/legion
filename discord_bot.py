"""Minimal Discord bridge for Legion actions."""

import asyncio
import json
import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("BRIDGE_CHANNEL_ID", "1362902052279291904"))


class BridgeClient(discord.Client):
    async def on_ready(self):
        print(f"Bridge logged in as {self.user}")

    async def post_action(self, action: dict) -> None:
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(json.dumps(action))


def send_action(action: dict) -> None:
    client = BridgeClient(intents=discord.Intents.default())

    async def runner():
        await client.login(TOKEN)
        await client.connect()
        await client.post_action(action)
        await client.close()

    asyncio.run(runner())


if __name__ == "__main__":
    sample = {"type": "test", "detail": "bridge operational"}
    send_action(sample)
