import unittest

import pytest

from legion.agents.python.architect import ArchitectAgent
from legion.agents.python.echo import EchoAgent
from legion.agents.python.healthcheck import HealthcheckAgent
from legion.agents.python.metrics import MetricsAgent
from legion.agents.python.ping import PingAgent
from legion.agents.python.therapist import TherapistAgent
from legion.agents.python.ux_designer import UxDesignerAgent
from memory.legion_memory import LegionAgentMemory

AGENT_CLASSES = [
    ArchitectAgent,
    EchoAgent,
    HealthcheckAgent,
    PingAgent,
    TherapistAgent,
    UxDesignerAgent,
    MetricsAgent,
]


class DummyOrchestrator:
    agent_channel_ids = {
        cls.__name__.replace("Agent", "").lower() + "_agent": 1 for cls in AGENT_CLASSES
    }
    client = None
    config = {}

    def __init__(self):
        self.config = {}
        for agent_name in self.agent_channel_ids:
            self.config[agent_name] = {"repo_path": "."}


def make_agent(agent_cls):
    agent = agent_cls(DummyOrchestrator(), None)
    agent.memory = LegionAgentMemory(agent.name)
    agent.name = agent_cls.__name__.replace("Agent", "").lower() + "_agent"
    return agent


@pytest.mark.parametrize("agent_cls", AGENT_CLASSES)
def test_agent_memory_persistence_and_retrieval(agent_cls):
    agent = make_agent(agent_cls)
    # Store first message
    msg1 = f"hello from {agent.name}"
    agent.memory.log_task({"type": "user_message", "content": msg1})
    # Retrieve and check
    memories = agent.memory.get_task_log()
    assert any(msg1 in str(m) for m in memories)
    # Store second message
    msg2 = f"second message for {agent.name}"
    agent.memory.log_task({"type": "user_message", "content": msg2})
    memories2 = agent.memory.get_task_log()
    assert any(msg2 in str(m) for m in memories2)
    # Ensure both messages are present
    assert len(memories2) >= 2


def test_agent_memory_persistence_across_reload():
    agent = make_agent(ArchitectAgent)
    msg = "persisted across reload"
    agent.memory.log_task({"type": "user_message", "content": msg})
    # Simulate reload by creating a new agent with the same name
    agent2 = make_agent(ArchitectAgent)
    memories = agent2.memory.get_task_log()
    assert any(msg in str(m) for m in memories)


def test_cross_agent_memory_isolation():
    agent1 = make_agent(ArchitectAgent)
    agent2 = make_agent(TherapistAgent)
    msg1 = "architect secret"
    msg2 = "therapist secret"
    agent1.memory.log_task({"type": "user_message", "content": msg1})
    agent2.memory.log_task({"type": "user_message", "content": msg2})
    mem1 = agent1.memory.get_task_log()
    mem2 = agent2.memory.get_task_log()
    assert any(msg1 in str(m) for m in mem1)
    assert not any(msg2 in str(m) for m in mem1)
    assert any(msg2 in str(m) for m in mem2)
    assert not any(msg1 in str(m) for m in mem2)


@unittest.skip("legacy failure – deferred")
class LegacyPlaceHolder(unittest.TestCase):
    pass
