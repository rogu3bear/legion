#!/usr/bin/env bash

set -euo pipefail

# Source environment variables if .env exists
if [ -f .env ]; then
    source .env
fi

# Validate required environment variables
required_vars=("DISCORD_TOKEN" "ORCH_CONFIG_PATH" "DISCORD_CHANNELS_PATH")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "[ERROR] $var is not set. Please set it in your environment or .env file."
        exit 1
    fi
done

# Set up Python path
export PYTHONPATH="$(pwd)"

# Start the orchestrator
echo "[INFO] Starting Legion orchestrator..."
exec python -m legion.orchestrator 