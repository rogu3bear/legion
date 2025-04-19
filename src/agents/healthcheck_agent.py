from src.agents.base_agent import BaseAgent
import asyncio
import time

class HealthcheckAgent(BaseAgent):
    def __init__(self, name, config=None, channel=None):
        super().__init__(name, config, channel)
        self.start_time = time.time()

    async def start(self):
        asyncio.create_task(self._health_loop())

    async def _health_loop(self):
        while True:
            uptime = int(time.time() - self.start_time)
            msg = await self.channel.send(f"Uptime: {uptime}s")
            threshold = self.config.get("uptime_threshold_minutes", 0) * 60
            if uptime >= threshold:
                await msg.add_reaction("✅")
                self.memory.log_task({"type": "health_success", "uptime": uptime})
            else:
                await msg.add_reaction("⚠️")
                self.memory.log_task({"type": "health_failure", "uptime": uptime})
            await asyncio.sleep(self.config.get("check_interval_minutes", 5) * 60) 