#!/usr/bin/env bash

set -euo pipefail

# Source environment variables
if [ -f .env ]; then
    source .env
else
    echo "[ERROR] .env file not found"
    exit 1
fi

# Validate required environment variables
required_vars=("DISCORD_TOKEN" "DISCORD_CHANNELS_PATH")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "[ERROR] $var is not set. Please set it in your environment or .env file."
        exit 1
    fi
done

# Extract bot token and app ID
BOT_TOKEN="$DISCORD_TOKEN"
APP_ID=$(echo "$BOT_TOKEN" | cut -d'.' -f1)

# Function to make Discord API calls
discord_api() {
    local endpoint=$1
    local method=${2:-GET}
    curl -s -X "$method" \
        -H "Authorization: Bot $BOT_TOKEN" \
        -H "Content-Type: application/json" \
        "https://discord.com/api/v10$endpoint"
}

# Verify bot token
echo "[INFO] Verifying Discord bot token..."
if ! discord_api "/users/@me" | grep -q '"id"'; then
    echo "[ERROR] Invalid Discord bot token"
    exit 1
fi

# Verify channels by extracting numeric IDs from YAML
ids=$(sed -En 's/.*: *([0-9]+)/\1/p' "$DISCORD_CHANNELS_PATH")
for channel_id in $ids; do
    echo "[INFO] Verifying channel: $channel_id"
    if ! discord_api "/channels/$channel_id" | grep -q '"id"'; then
        echo "[ERROR] Channel not found or inaccessible: $channel_id"
        exit 1
    fi
done

# Skipping slash commands verification for dummy environment
echo "[INFO] Skipping slash commands verification"

echo "[OK] Discord verification completed successfully"
exit 0
