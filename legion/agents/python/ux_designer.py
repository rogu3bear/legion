from legion.agents.base import BaseAgent
from core.therapist import therapist_guard


class UxDesignerAgent(BaseAgent):
    system_prompt = """
    You are 🎨 the UX Designer Agent—critique, improve, and propose user experience and interface designs for all Legion features.
    """

    def __init__(self, name: str, config: dict, orchestrator_ref=None, llm_client=None):
        super().__init__(name, config or {}, llm_client=llm_client)
        # retain orchestrator reference
        self.orchestrator = orchestrator_ref

    # All message handling is now inherited from BaseAgent.

    @therapist_guard("directive")
    async def handle_critique(self):
        return await self.handle_message(
            content="Please critique the current user experience and suggest improvements.",
            author=self.name,
            timestamp=None,
        )
