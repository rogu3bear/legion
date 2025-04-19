from src.agents.base_agent import BaseAgent
import asyncio

class PingAgent(BaseAgent):
    async def start(self):
        asyncio.create_task(self._ping_loop())

    async def _ping_loop(self):
        while True:
            await self.channel.send("ping?")
            # Assume metrics_agent is globally accessible or injected
            self.memory.log_task({"type": "ping_sent"})
            await asyncio.sleep(60)

    async def on_message(self, message):
        if message.content == "pong":
            self.memory.log_task({"type": "pong_received"}) 