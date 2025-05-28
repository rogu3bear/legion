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
required_vars=("ORCH_CONFIG_PATH")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "[ERROR] $var is not set. Please set it in your environment or .env file."
        exit 1
    fi
done

# Create memory directory
echo "[INFO] Creating memory directory..."
mkdir -p memory/db

# Initialize vector store
echo "[INFO] Initializing vector store..."
if ! python -m legion.core.init_memory; then
    echo "[ERROR] Failed to initialize vector store"
    exit 1
fi

# Verify memory connectivity
echo "[INFO] Verifying memory connectivity..."
if ! python -c "
from legion.core.memory import Memory
memory = Memory()
memory.write('test', 'test')
result = memory.read('test')
if result != 'test':
    raise Exception('Memory verification failed')
"; then
    echo "[ERROR] Memory verification failed"
    exit 1
fi

echo "[OK] Memory initialization completed successfully"
exit 0
