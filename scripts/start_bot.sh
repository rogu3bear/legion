#!/usr/bin/env bash
# set up our module path and launch the Discord bot
MODEL=${OPENAI_MODEL:-meta-llama-3.1-8b-instruct}
if command -v lms >/dev/null 2>&1; then
  echo "[INFO] Ensuring LM Studio model is loaded: $MODEL"
  lms load "$MODEL" || echo "[WARN] lms load failed or not required."
fi
export PYTHONPATH="$(pwd)"
exec python3 -m integration.discord.bot 