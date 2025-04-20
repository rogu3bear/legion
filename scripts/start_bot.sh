#!/usr/bin/env bash
# set up our module path and launch the Discord bot
export PYTHONPATH="$(pwd)"
exec python3 -m integration.discord.bot 