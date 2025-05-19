from __future__ import annotations
"""Doctor agent stub.

Author: Codex
"""

from legion.agents.base import BaseAgent


class DoctorAgent(BaseAgent):
    """Medical assistant agent placeholder."""

    def __init__(self, name: str, config: dict, llm_client=None):
        super().__init__(name, config, llm_client)

    async def assess_patient(self, symptoms: str) -> str:
        """Return basic assessment (stub)."""
        symptoms_l = symptoms.lower()
        if "fever" in symptoms_l:
            return "Possible febrile condition."
        if "cough" in symptoms_l:
            return "Monitor for respiratory infection."
        return "Further analysis required."
