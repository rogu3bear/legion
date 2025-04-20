from legion.agents.base import BaseAgent


class UxDesignerAgent(BaseAgent):
    def __init__(self, name, client, channel_id, config=None):
        super().__init__(name, client, channel_id, config=config)

    # All message handling is now inherited from BaseAgent.
