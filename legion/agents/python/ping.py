from legion.agents.base import BaseAgent


class PingAgent(BaseAgent):
    """Always replies 'pong'."""

    system_prompt = """
    You are 📶 the Ping Agent—respond to health checks and connectivity tests with simple, reliable replies (e.g., 'pong').
    """

    def __init__(self, orchestrator, config=None, **kwargs):
        super().__init__(orchestrator, config=config)

    # All message handling is now inherited from BaseAgent.

    async def handle_ping(self):
        return await self.handle_message(
            content="ping", author=self.name, timestamp=None
        )
