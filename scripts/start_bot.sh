#!/bin/bash
# Change to project root
cd "$(dirname "$0")/.."
# Activate venv
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
else
  echo ".venv/bin/activate not found. Creating venv..."
  python3 -m venv .venv
  source .venv/bin/activate
fi
# Run the Discord bot
PYTHONPATH=. python src/discord_integration.py
