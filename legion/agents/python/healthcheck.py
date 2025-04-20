from legion.agents.base import BaseAgent


class HealthcheckAgent(BaseAgent):
    """Quick stub healthcheck: always returns OK."""
    system_prompt = """
    You are ✅ the Healthcheck Agent—perform and report on system health checks, ensuring all services are operational.
    """

    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        # For memory check, use a simple in-memory dict
        self._memory_test = {}

    # All message handling is now inherited from BaseAgent.

    # self_assess and handle_message removed; use BaseAgent defaults.

    async def handle_healthcheck(self):
        return await self.handle_message(
            content="Please perform a health check and report system status.",
            author=self.name,
            timestamp=None
        )
