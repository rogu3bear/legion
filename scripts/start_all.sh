#!/usr/bin/env bash
set -e

# Load base environment
if [ -f .env ]; then
    source .env
fi
# Load development-specific overrides
if [ -f .env.development ]; then
    source .env.development
fi

export LMSTUDIO_API_URL

# Validate internal ports (excluding LMStudio port 1234)
python - << 'PYCODE'
from legion.ports import load_runtime_ports
from legion.utils.port_conflict_checker import check_ports_available
ports = load_runtime_ports()
check_ports_available(ports)
PYCODE

# Start services
./scripts/start_bot.sh &
./scripts/start_web.sh &
wait 