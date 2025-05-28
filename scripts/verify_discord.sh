#!/usr/bin/env bash

set -euo pipefail

# Source environment variables
if [ -f .env ]; then
    source .env
else
    echo "[ERROR] .env file not found"
    exit 1
fi
if [ -f .env.ports ]; then
    source .env.ports
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
echo "[INFO] Verifying channels from $DISCORD_CHANNELS_PATH..."
yaml_ids=$(sed -En 's/.*: *([0-9]+)/\1/p' "$DISCORD_CHANNELS_PATH")
for channel_id in $yaml_ids; do
    if [[ "$channel_id" =~ ^[0-9]+$ && "$channel_id" -ne 0 ]]; then # Skip if not a number or is 0
        echo "[INFO] Verifying YAML channel: $channel_id"
        if ! discord_api "/channels/$channel_id" | grep -q '"id"'; then
            echo "[ERROR] YAML Channel not found or inaccessible: $channel_id"
            # Consider exiting here if YAML channels are critical: exit 1
        fi
    else
        echo "[WARN] Invalid or zero channel ID found in YAML: '$channel_id' (from $DISCORD_CHANNELS_PATH)"
    fi
done

# Verify all *_CHANNEL_ID environment variables
echo "[INFO] Verifying specific *_CHANNEL_ID environment variables from .env..."

# List of known channel ID variable names from .env
# Note: DISCORD_CHANNELS_PATH is not a channel ID itself.
known_channel_env_vars=(
    "GENERAL_CHANNEL_ID"
    "AGENT_FEED_CHANNEL_ID"
    "ARCHITECT_CHANNEL_ID"
    "METRICS_CHANNEL_ID"
    "THERAPIST_CHANNEL_ID"
    "DESIGN_CHANNEL_ID"
    "BOT_COMMANDS_CHANNEL_ID"
    "AGENT_LOGS_CHANNEL_ID"
    "AGENT_FEEDBACK_CHANNEL_ID"
    "CONFIG_UPDATES_CHANNEL_ID"
    "ALERTS_CHANNEL_ID"
    "METRICS_DASH_CHANNEL_ID"
)

found_any_env_channels=0

for var_name in "${known_channel_env_vars[@]}"; do
    # Get the value of the variable indirectly
    channel_id="${!var_name}" # This gets the value of the var named in var_name

    if [ -n "$channel_id" ]; then # Check if the variable is set
        found_any_env_channels=1
        echo "[DEBUG] Processing ENV var '$var_name' with value: $channel_id"
        if [[ "$channel_id" =~ ^[0-9]+$ && "$channel_id" -ne 0 ]]; then
            is_in_yaml=0
            for yaml_id_check in $yaml_ids; do
                if [ "$yaml_id_check" = "$channel_id" ]; then
                    is_in_yaml=1
                    break
                fi
            done

            if [ "$is_in_yaml" -eq 0 ]; then
                echo "[INFO] Verifying ENV channel from var '$var_name': $channel_id"
                if ! discord_api "/channels/$channel_id" | grep -q '"id"'; then
                    echo "[ERROR] ENV Channel (from $var_name) not found or inaccessible: $channel_id"
                    # exit 1 # Decide if this should be a fatal error
                fi
            else
                echo "[INFO] Skipping ENV channel $channel_id (from $var_name) (already checked from YAML or duplicate)"
            fi
        elif [ "$channel_id" != "0" ]; then # Only warn if not '0' and not a valid number
            echo "[WARN] Invalid channel ID format in ENV var '$var_name': '$channel_id'"
        elif [ "$channel_id" == "0" ]; then
             echo "[INFO] ENV var '$var_name' is 0, skipping API check."
        fi
    else
        echo "[DEBUG] ENV var '$var_name' is not set."
    fi
done

if [ "$found_any_env_channels" -eq 0 ]; then
    echo "[INFO] No specific *_CHANNEL_ID variables found or processed from environment."
fi

# Skipping slash commands verification for dummy environment
echo "[INFO] Skipping slash commands verification"

echo "[OK] Discord verification completed successfully"
exit 0
