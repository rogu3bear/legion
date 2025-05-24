"""Minimal Discord bridge for Legion actions."""

import asyncio
import json
import os
import time

import discord
from dotenv import load_dotenv

load_dotenv(override=True)

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("AGENT_FEED_CHANNEL_ID"))  # Use the exact channel ID from env vars

print(f"[DEBUG] Using token starting with: {TOKEN[:12]}...")
print(f"[DEBUG] Using channel ID: {CHANNEL_ID}")

intents = discord.Intents.default()
intents.message_content = True


class BridgeBot(discord.Client):
    def __init__(self, action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = action
        self.success = False

    async def on_ready(self):
        print(f"Bot is ready! Logged in as {self.user}")

        # Find the channel
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            print(f"Found channel: {channel.name}")
            try:
                # Send the action as JSON
                json_text = json.dumps(self.action)
                await channel.send(json_text)
                print(f"JSON action sent successfully: {json_text}")
                self.success = True
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print(f"Could not find channel with ID {CHANNEL_ID}")
            # List available channels
            print("Available channels:")
            for guild in self.guilds:
                print(f"Guild: {guild.name}")
                for ch in guild.text_channels:
                    print(f"  - {ch.name} (ID: {ch.id})")

        # Close the client after sending the message
        await self.close()


def send_action(action):
    """Send an action dictionary to Discord."""
    client = BridgeBot(action, intents=intents)
    try:
        client.run(TOKEN)
        return client.success
    except Exception as e:
        print(f"Error running bot: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    sample = {"type": "test", "detail": "bridge operational", "timestamp": time.time()}
    print(f"Sending action: {sample}")
    result = send_action(sample)
    print(f"Action sent: {result}")
