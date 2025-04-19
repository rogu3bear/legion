import pytest
from legion.orchestrator import Orchestrator

def test_test_agents_registered():
    """Tests that test agents are registered in the orchestrator."""
    orch = Orchestrator()
    for agent in ["ping_agent", "echo_agent", "healthcheck_agent"]:
        assert agent in orch.agent_channel_ids 

def test_orchestrator_stub():
    assert True 