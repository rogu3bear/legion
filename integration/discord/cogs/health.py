"""Health cog stub for Discord integration."""

import asyncio
import time
from typing import Optional

import discord


class HealthCog:
    pass


class HealthcheckAgent:
    """Simple healthcheck agent that reports uptime."""

    def __init__(
        self,
        name: str,
        config: Optional[dict] = None,
        channel: Optional[discord.abc.Messageable] = None,
        memory=None,
    ) -> None:
        self.name = name
        self.config = config or {}
        self.channel = channel
        self.memory = memory
        self.start_time = time.time()
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Starts the health check background loop."""
        self._task = asyncio.create_task(self._health_loop())

    async def _health_loop(self) -> None:
        """Periodically checks uptime and logs health status."""
        while True:
            uptime = int(time.time() - self.start_time)
            if self.channel is not None:
                msg = await self.channel.send(f"Uptime: {uptime}s")
                threshold = self.config.get("uptime_threshold_minutes", 0) * 60
                if uptime >= threshold:
                    await msg.add_reaction("✅")
                    if self.memory is not None:
                        self.memory.log_task(
                            {"type": "health_success", "uptime": uptime}
                        )
                else:
                    await msg.add_reaction("⚠")
                    if self.memory is not None:
                        self.memory.log_task(
                            {"type": "health_failure", "uptime": uptime}
                        )
            await asyncio.sleep(self.config.get("check_interval_minutes", 5) * 60)
