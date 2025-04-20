from legion.agents.base import BaseAgent


class ResearcherAgent(BaseAgent):
    """Stub for ResearcherAgent."""

    system_prompt = """
    You are 🧑‍🔬 the Researcher Agent—investigate, gather, and synthesize information to support the team's goals and answer technical questions.
    """

    def __init__(self, orchestrator):
        super().__init__(orchestrator)

    # All message handling is now inherited from BaseAgent.
