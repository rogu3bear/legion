from legion.agents.base import BaseAgent


class DoctorAgent(BaseAgent):
    """Stub for DoctorAgent."""
    system_prompt = """
    You are 🩺 the Doctor Agent—diagnose, triage, and prescribe solutions for code and system health issues.
    """

    def __init__(self, orchestrator):
        super().__init__(orchestrator)

    # All message handling is now inherited from BaseAgent.
