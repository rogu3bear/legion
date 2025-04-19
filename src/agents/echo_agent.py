from src.agents.base_agent import BaseAgent

class EchoAgent(BaseAgent):
    async def on_message(self, message):
        if message.channel.id == self.channel.id and message.content.startswith("!echo "):
            text = message.content[len("!echo "):]
            await self.channel.send(f"{self.config.get('echo_prefix', '[echo]')} {text}")
            self.memory.log_task({"type": "echo_response", "text": text})
            metrics_agent.record("echo_responses") 