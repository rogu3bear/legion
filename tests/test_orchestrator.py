import pytest
from src.orchestrator import Orchestrator

def test_test_agents_registered():
    orch = Orchestrator()
    for agent in ["ping_agent", "echo_agent", "healthcheck_agent"]:
        assert agent in orch.agent_channel_ids 