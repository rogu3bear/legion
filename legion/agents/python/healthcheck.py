from legion.agents.base import BaseAgent


class HealthcheckAgent(BaseAgent):
    """Quick stub healthcheck: always returns OK."""

    def __init__(self, name, client, channel_id, config=None):
        super().__init__(name, client, channel_id, config=config)
        # For memory check, use a simple in-memory dict
        self._memory_test = {}

    # All message handling is now inherited from BaseAgent.

    # self_assess and handle_message removed; use BaseAgent defaults.
