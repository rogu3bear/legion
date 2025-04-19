class DoctorAgent:
    """Stub for DoctorAgent."""
    def on_message(self, message):
        pass

    async def on_message(self, message):
        """Handles "!echo" messages in a Discord channel, echoes back, logs, and records metrics."""
        if message.channel.id == self.channel.id and message.content.startswith("!echo "):
            text = message.content[len("!echo "):]
            await self.channel.send(f"{self.config.get('echo_prefix', '[echo]')} {text}")
            self.memory.log_task({"type": "echo_response", "text": text})
            metrics_agent.record("echo_responses") 