import pytest

from legion.agents.python.architect import ArchitectAgent
from legion.core.prompt_builder import PromptBuilder


class DummyOrch:
    agent_channel_ids = {"architect_agent": 1}

    def __init__(self):
        self.config = {"architect_agent": {"repo_path": "."}}

    def __str__(self):
        return "DummyOrch"


@pytest.mark.asyncio
async def test_prompt_builder_simple():
    system_prompt = "sys"
    memories = ["m1", "m2"]
    history = [{"role": "user", "content": "hi"}]
    user_query = "query"
    msgs = PromptBuilder.build(system_prompt, memories, history, user_query)
    assert msgs[0]["content"] == "sys"
    assert msgs[1]["content"].startswith("Previously on our project:")
    assert msgs[-1] == {"role": "user", "content": "query"}


@pytest.mark.asyncio
async def test_architect_handle_review_override(monkeypatch):
    # Stub call_llm and post_to_discord
    agent = ArchitectAgent(DummyOrch())
    agent.config = {"model": "x", "review_temperature": 0.7, "review_max_tokens": 100}
    called = {}

    def fake_call_llm(thread_id, history, **kwargs):
        called["thread_id"] = thread_id
        called["history"] = history
        called["kwargs"] = kwargs
        return "res"

    monkeypatch.setattr(agent, "call_llm", fake_call_llm)
    posted = []

    async def fake_post(msg):
        posted.append(msg)

    monkeypatch.setattr(agent, "post_to_discord", fake_post)

    await agent.handle_review()
    # Validate overrides
    assert called["thread_id"] == "review"
    assert called["kwargs"]["model"] == "x"
    assert called["kwargs"]["temperature"] == 0.7
    assert called["kwargs"]["max_tokens"] == 100
    # Ensure post_to_discord was called
    assert posted == ["res"]
