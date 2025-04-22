from legion.agents.base import BaseAgent


class EchoAgent(BaseAgent):
    """Echoes back the incoming text."""

    system_prompt = """
    You are 🔁 the Echo Agent—repeat back any message you receive, useful for diagnostics and testing message flow.
    """

    def __init__(self, orchestrator):
        super().__init__(orchestrator)

    # All message handling is now inherited from BaseAgent.

    # self_assess and handle_message removed; use BaseAgent defaults.

    async def handle_echo(self, message):
        return await self.handle_message(
            content=message, author=self.name, timestamp=None
        )
