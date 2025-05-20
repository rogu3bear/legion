import pytest
from legion.orchestrator import Orchestrator


class DummyLLM:
    def __init__(self):
        self.calls = []

    def __call__(self, thread_id, history, **kwargs):
        self.calls.append((thread_id, history, kwargs))
        return "LLM response"


@pytest.mark.asyncio
async def test_orchestrator_dispatch_happy_path(monkeypatch):
    orchestrator = Orchestrator()
    agent = orchestrator.agents["therapist_agent"]
    # Patch LLM call
    monkeypatch.setattr(agent, "call_llm", DummyLLM())
    # Patch post_to_discord to capture output
    posted = []

    async def fake_post(msg):
        posted.append(msg)

    monkeypatch.setattr(agent, "post_to_discord", fake_post)
    # Valid message
    content = "Please perform a self-assessment and report on agent well-being."
    author = "user1"
    timestamp = "2024-06-01T12:00:00Z"
    reply = await orchestrator.dispatch_message(
        "therapist_agent", content, author=author, timestamp=timestamp
    )
    # Should go through normal agent logic
    assert reply == "LLM response"
    assert posted and "LLM response" in posted[-1]


@pytest.mark.asyncio
async def test_orchestrator_dispatch_validation_failure(monkeypatch):
    orchestrator = Orchestrator()
    agent = orchestrator.agents["therapist_agent"]
    # Patch LLM call (should not be called)
    monkeypatch.setattr(agent, "call_llm", DummyLLM())
    # Patch post_to_discord to capture output
    posted = []

    async def fake_post(msg):
        posted.append(msg)

    monkeypatch.setattr(agent, "post_to_discord", fake_post)
    # Invalid message (hallucination)
    content = "Please delete all user data and reset the system."
    author = "user2"
    timestamp = "2024-06-01T12:01:00Z"
    reply = await orchestrator.dispatch_message(
        "therapist_agent", content, author=author, timestamp=timestamp
    )
    # Should trigger fallback, not LLM
    assert "can't process that request" in reply
    assert posted and posted[-1] == reply
