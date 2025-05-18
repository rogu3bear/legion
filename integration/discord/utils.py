"""Shared Discord helper utilities."""

import logging
from typing import List

import discord


async def fetch_thread_history(channel: discord.abc.Messageable, thread: discord.abc.Messageable, limit: int) -> List[discord.Message]:
    """Return the last ``limit`` messages from a thread or channel."""
    try:
        history_obj = thread if hasattr(thread, "history") else channel
        messages = []
        history = history_obj.history(limit=limit)
        if hasattr(history, "__await__"):
            history = await history
        async for msg in history:
            messages.append(msg)
        return list(reversed(messages))
    except Exception as e:  # pragma: no cover - network/permission issues
        logging.warning(f"[fetch_thread_history] Failed to fetch thread history: {e}")
        return []
