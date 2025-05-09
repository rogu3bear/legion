from legion.agents.base import BaseAgent


class UxDesignerAgent(BaseAgent):
    system_prompt = """
    You are 🎨 the UX Designer Agent—critique, improve, and propose user experience and interface designs for all Legion features.
    """

    def __init__(self, orchestrator, llm_client=None):
        super().__init__(orchestrator, llm_client=llm_client)

    # All message handling is now inherited from BaseAgent.

    async def handle_critique(self):
        return await self.handle_message(
            content="Please critique the current user experience and suggest improvements.",
            author=self.name,
            timestamp=None,
        )
