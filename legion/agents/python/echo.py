from legion.agents.base import BaseAgent


class EchoAgent(BaseAgent):
    """Echoes back the incoming text."""

    def __init__(self, name, client, channel_id, config=None):
        super().__init__(name, client, channel_id, config=config)

    # All message handling is now inherited from BaseAgent.

    # self_assess and handle_message removed; use BaseAgent defaults.
