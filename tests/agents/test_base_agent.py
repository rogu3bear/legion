import pytest
import datetime
import asyncio
import os
from legion.agents.python.architect import ArchitectAgent
from legion.agents.python.doctor import DoctorAgent
from legion.agents.python.echo import EchoAgent
from legion.agents.python.healthcheck import HealthcheckAgent
from legion.agents.python.ping import PingAgent
from legion.agents.python.researcher import ResearcherAgent
from legion.agents.python.therapist import TherapistAgent
from legion.agents.python.ux_designer import UxDesignerAgent
from memory.legion_memory import LegionAgentMemory
from integration.discord.bot import fetch_thread_history
from legion.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_echo_agent_handle_message_payload_and_memory(monkeypatch):
    # Setup EchoAgent with stubbed config and dummy client
    class DummyClient:
        def get_channel(self, channel_id):
            # Not used due to stubbed fetch_thread_history
            return None

    config = {
        "default_prompt": "You are a test agent.",
        "memory_top_k": 2,
        "history_limit": 3,
        "embedding_model": "test-embed-model",
    }
    agent = EchoAgent("echo_agent", DummyClient(), 123, config=config)

    # Stub get_message_embedding
    monkeypatch.setattr(agent, "get_message_embedding", lambda text: [0.1, 0.2])
    # Stub retrieve_memories
    retrieved = ["mem1", "mem2"]
    monkeypatch.setattr(agent, "retrieve_memories", lambda name, emb, k: retrieved)
    # Stub fetch_thread_history
    stub_history = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]
    fut = asyncio.Future()
    fut.set_result(stub_history)
    monkeypatch.setattr(agent, "fetch_thread_history", lambda ch, tid, lim: fut)
    # Capture payload to call_llm
    captured = {}

    def fake_call_llm(thread_id, messages, **kwargs):
        captured["thread_id"] = thread_id
        captured["messages"] = messages
        return "reply"

    monkeypatch.setattr(agent, "call_llm", fake_call_llm)
    # Stub post_to_discord to avoid real Discord calls
    posted = []

    async def fake_post(msg):
        posted.append(msg)

    monkeypatch.setattr(agent, "post_to_discord", fake_post)
    # Stub extract_memories
    new_mems = ["new1"]
    monkeypatch.setattr(agent, "extract_memories", lambda text: new_mems)
    # Stub store_memories
    stored = {}

    def fake_store(name, mems):
        stored["agent_name"] = name
        stored["mems"] = mems

    monkeypatch.setattr(agent, "store_memories", fake_store)

    # Call handle_message
    context = {
        "content": "test content",
        "author": "user",
        "timestamp": datetime.datetime(2020, 1, 1, 0, 0),
    }
    await agent.handle_message(context)

    # Construct expected payload
    expected_messages = [
        {"role": "system", "content": "You are a test agent."},
        {"role": "system", "content": "Relevant memories:\n- mem1\n- mem2"},
        *stub_history,
        {"role": "user", "content": "test content"},
    ]
    assert captured.get("messages") == expected_messages
    assert stored.get("agent_name") == "echo_agent"
    assert stored.get("mems") == new_mems


def test_legion_agent_memory_vector_store(tmp_path, monkeypatch):
    # Use a temp directory for isolation
    base_dir = tmp_path / "memory"
    agent_name = "test_agent"
    os.makedirs(base_dir / agent_name, exist_ok=True)
    # 1. Empty store returns []
    res = LegionAgentMemory.retrieve_memories(
        agent_name, [1.0, 0.0], 3, base_dir=str(base_dir)
    )
    assert res == []
    # 2. Normal store/search
    snippets = [
        {"text": "foo", "embedding": [1.0, 0.0]},
        {"text": "bar", "embedding": [0.0, 1.0]},
        {"text": "baz", "embedding": [0.7, 0.7]},
    ]
    LegionAgentMemory.store_memories(agent_name, snippets, base_dir=str(base_dir))
    # Query for [1,0] should return 'foo' first
    out = LegionAgentMemory.retrieve_memories(
        agent_name, [1.0, 0.0], 2, base_dir=str(base_dir)
    )
    assert out[0] == "foo"
    # Query for [0,1] should return 'bar' first
    out2 = LegionAgentMemory.retrieve_memories(
        agent_name, [0.0, 1.0], 2, base_dir=str(base_dir)
    )
    assert out2[0] == "bar"
    # 3. Store error scenario: monkeypatch open to throw
    called = {"fail": 0}

    def fail_open(*a, **kw):
        called["fail"] += 1
        raise IOError("fail")

    monkeypatch.setattr("builtins.open", fail_open)
    LegionAgentMemory.store_memories(
        agent_name, [{"text": "fail", "embedding": [0, 0]}], base_dir=str(base_dir)
    )
    # Should have retried once (called twice)
    assert called["fail"] == 2


@pytest.mark.asyncio
async def test_fetch_thread_history_empty(monkeypatch):
    class DummyHistory:
        async def history(self, limit):
            return
            yield  # never yields

    dummy = DummyHistory()
    out = await fetch_thread_history(dummy, dummy, 5)
    assert out == []


@pytest.mark.asyncio
async def test_fetch_thread_history_partial(monkeypatch):
    class DummyMsg:
        def __init__(self, content):
            self.content = content

    class DummyHistory:
        async def history(self, limit):
            for i in range(min(limit, 3)):
                yield DummyMsg(f"msg{i}")

    dummy = DummyHistory()
    out = await fetch_thread_history(dummy, dummy, 5)
    assert [m.content for m in out] == ["msg2", "msg1", "msg0"]


@pytest.mark.asyncio
async def test_fetch_thread_history_error(monkeypatch):
    class DummyHistory:
        async def history(self, limit):
            raise Exception("rate limit!")

    dummy = DummyHistory()
    out = await fetch_thread_history(dummy, dummy, 5)
    assert out == []


@pytest.mark.asyncio
async def test_agent_smoke_all_inherit(monkeypatch):
    class DummyClient:
        def get_channel(self, channel_id):
            class DummyChan:
                async def history(self, limit):
                    return
                    yield

            return DummyChan()

    agents = [
        ArchitectAgent("architect", DummyClient(), 1),
        DoctorAgent("doctor", DummyClient(), 2),
        EchoAgent("echo", DummyClient(), 3),
        HealthcheckAgent("health", DummyClient(), 4),
        PingAgent("ping", DummyClient(), 5),
        ResearcherAgent("researcher", DummyClient(), 6),
        TherapistAgent("therapist", DummyClient(), 7),
        UxDesignerAgent("ux", DummyClient(), 8),
    ]
    # Patch get_message_embedding to avoid OpenAI call
    monkeypatch.setattr(
        ArchitectAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        DoctorAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        EchoAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        HealthcheckAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        PingAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        ResearcherAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        TherapistAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        UxDesignerAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    # Patch retrieve_memories to avoid file IO
    monkeypatch.setattr(
        ArchitectAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )
    monkeypatch.setattr(
        DoctorAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )
    monkeypatch.setattr(
        EchoAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )
    monkeypatch.setattr(
        HealthcheckAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )
    monkeypatch.setattr(
        PingAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )
    monkeypatch.setattr(
        ResearcherAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )
    monkeypatch.setattr(
        TherapistAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )
    monkeypatch.setattr(
        UxDesignerAgent, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )

    # Patch fetch_thread_history to avoid Discord API
    async def fake_history(self, channel_id, thread_id, limit):
        return []

    for agent in agents:
        monkeypatch.setattr(agent, "fetch_thread_history", fake_history.__get__(agent))
        monkeypatch.setattr(agent, "call_llm", lambda thread_id, messages: "ok")
        monkeypatch.setattr(agent, "post_to_discord", lambda msg: None)
        monkeypatch.setattr(agent, "extract_memories", staticmethod(lambda text: []))
        monkeypatch.setattr(
            agent, "store_memories", staticmethod(lambda name, mems: None)
        )
    # Should not raise
    for agent in agents:
        context = {
            "content": "hi",
            "author": "user",
            "timestamp": datetime.datetime.now(),
        }
        await agent.handle_message(context)


def test_helper_names_exist():
    from integration.discord.bot import fetch_thread_history
    from memory.legion_memory import retrieve_memories, store_memories

    assert callable(fetch_thread_history)
    assert callable(retrieve_memories)
    assert callable(store_memories)


def test_dispatch_message_with_context(monkeypatch):
    class DummyAgent(EchoAgent):
        async def handle_message(self, context):
            self.called = True
            return "ok"

    orch = Orchestrator()
    agent = DummyAgent("echo", None, 1)
    orch._agent_objects["echo"] = agent
    context = {
        "channel_id": 1,
        "thread_id": 1,
        "content": "hi",
        "author": "user",
        "timestamp": datetime.datetime.now(),
    }
    # Should not raise
    result = asyncio.get_event_loop().run_until_complete(
        orch.dispatch_message("echo", context)
    )
    assert result == "ok"
    assert getattr(agent, "called", False)
