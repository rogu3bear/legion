#!/usr/bin/env bash
# Verify Discord bot token and channel IDs

set -e

if [ -z "$DISCORD_TOKEN" ]; then
  echo "[ERROR] DISCORD_TOKEN is not set in your environment or .env file."
  exit 1
fi

cat <<EOF > verify_discord_ping.py
import os
import sys
import asyncio
from discord import Client, Intents

token = os.getenv('DISCORD_TOKEN')
if not token:
    print('[ERROR] DISCORD_TOKEN is not set.')
    sys.exit(1)

intents = Intents.default()

class PingClient(Client):
    async def on_ready(self):
        print(f'[OK] Connected as {self.user} (ID: {self.user.id})')
        await self.close()
    async def on_error(self, event, *args, **kwargs):
        print(f'[ERROR] Discord event error: {event}')
        await self.close()

try:
    client = PingClient(intents=intents)
    asyncio.run(client.start(token))
except Exception as e:
    print(f'[ERROR] Could not connect to Discord: {e}')
    sys.exit(1)
EOF

python3 verify_discord_ping.py
status=$?
rm -f verify_discord_ping.py
exit $status
