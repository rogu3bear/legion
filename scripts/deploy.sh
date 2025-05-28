#!/usr/bin/env bash

set -euo pipefail

# Source environment variables
if [ -f .env ]; then
    source .env
fi
if [ -f .env.ports ]; then
    source .env.ports
fi

# Validate required environment variables
required_vars=("DISCORD_TOKEN" "ORCH_CONFIG_PATH" "DISCORD_CHANNELS_PATH")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "[ERROR] $var is not set. Please set it in your environment or .env file."
        exit 1
    fi
done

# Create logs directory
mkdir -p scripts/logs
LOG_FILE="scripts/logs/deploy_$(date +%Y%m%d_%H%M%S).log"

echo "[INFO] Starting deployment..." | tee -a "$LOG_FILE"

# Step 1: Initialize memory
echo "[INFO] Initializing memory..." | tee -a "$LOG_FILE"
if ! ./scripts/init_memory.sh >> "$LOG_FILE" 2>&1; then
    echo "[ERROR] Memory initialization failed" | tee -a "$LOG_FILE"
    exit 1
fi

# Step 2: Run database migrations (if any)
echo "[INFO] Running database migrations..." | tee -a "$LOG_FILE"
if [ -f "scripts/migrate.sh" ]; then
    if ! ./scripts/migrate.sh >> "$LOG_FILE" 2>&1; then
        echo "[ERROR] Database migration failed" | tee -a "$LOG_FILE"
        exit 1
    fi
fi

# Step 3: Start the bot in background
echo "[INFO] Starting bot..." | tee -a "$LOG_FILE"
./scripts/start_bot.sh >> "$LOG_FILE" 2>&1 &
BOT_PID=$!

# Wait for bot to start (30 second timeout)
echo "[INFO] Waiting for bot to start..." | tee -a "$LOG_FILE"
TIMEOUT=30
while [ $TIMEOUT -gt 0 ]; do
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "[OK] Bot health check passed" | tee -a "$LOG_FILE"
        break
    fi
    sleep 1
    TIMEOUT=$((TIMEOUT - 1))
done

if [ $TIMEOUT -eq 0 ]; then
    echo "[ERROR] Bot failed to start within 30 seconds" | tee -a "$LOG_FILE"
    kill $BOT_PID
    exit 1
fi

# Step 4: Verify Discord setup
echo "[INFO] Verifying Discord setup..." | tee -a "$LOG_FILE"
if ! ./scripts/verify_discord.sh >> "$LOG_FILE" 2>&1; then
    echo "[ERROR] Discord verification failed" | tee -a "$LOG_FILE"
    kill $BOT_PID
    exit 1
fi

# Step 5: Run integration tests
echo "[INFO] Running integration tests..." | tee -a "$LOG_FILE"
if ! pytest tests/discord/ tests/integration/ --maxfail=1 -v >> "$LOG_FILE" 2>&1; then
    echo "[ERROR] Integration tests failed" | tee -a "$LOG_FILE"
    kill $BOT_PID
    exit 1
fi

echo "[SUCCESS] Deployment completed successfully" | tee -a "$LOG_FILE"
kill $BOT_PID
exit 0
