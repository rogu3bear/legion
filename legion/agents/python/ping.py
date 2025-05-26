from legion.agents.base import BaseAgent


class PingAgent(BaseAgent):
    """Always replies 'pong'."""

    system_prompt = """
    You are 📶 the Ping Agent—respond to health checks and connectivity tests with simple, reliable replies (e.g., 'pong').
    """

    def __init__(self, name: str = "ping", config: dict = None, orchestrator_ref=None, llm_client=None):
        super().__init__(name=name, config=config or {}, llm_client=llm_client)
        self.orchestrator = orchestrator_ref

    # All message handling is now inherited from BaseAgent.

    async def handle_ping(self):
        return await self.handle_message(
            content="ping", author=self.name, timestamp=None
        )

    async def handle_task(self, payload: dict) -> dict:
        """Handle incoming tasks."""
        function_tag = payload.get("function_tag")
        
        if function_tag == "ping":
            result = await self.handle_ping()
            return {"status": "✅ Success", "result": result}
        else:
            return {"status": "❌ Unknown function_tag", "error": f"Unknown function_tag: {function_tag}"}
