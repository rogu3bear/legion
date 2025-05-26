"""Healthcheck agent implementation."""

from typing import Any, Optional

from legion.agents.base import BaseAgent


class HealthcheckAgent(BaseAgent):
    """Simple agent for health checks and system status monitoring."""

    system_prompt = (
        "You are ✅ the Healthcheck Agent—monitor system health and provide status reports."
    )

    def __init__(self, name: str = "healthcheck", config: Optional[dict] = None, orchestrator_ref: Optional[Any] = None, llm_client: Optional[Any] = None) -> None:
        super().__init__(name=name, config=config or {}, llm_client=llm_client)
        self.orchestrator = orchestrator_ref

    async def health_check(self) -> dict:
        """Perform a basic health check."""
        return {"status": "healthy", "timestamp": "now"}

    async def handle_task(self, payload: dict) -> dict:
        """Handle incoming tasks."""
        function_tag = payload.get("function_tag")
        
        if function_tag == "health_check":
            result = await self.health_check()
            return {"status": "✅ Success", "result": result}
        else:
            return {"status": "❌ Unknown function_tag", "error": f"Unknown function_tag: {function_tag}"} 