from src.legion_memory import LegionAgentMemory

class BaseAgent:
    def __init__(self, name, config=None, channel=None):
        self.name = name
        self.config = config or {}
        self.memory = LegionAgentMemory(name)
        self.channel = channel  # Discord channel object, to be set by orchestrator/bot
    async def start(self):
        pass
    async def on_message(self, message):
        pass 