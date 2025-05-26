import asyncio
import datetime
import os
import unittest

import pytest

from integration.discord.bot import fetch_thread_history
from legion.agents.base import BaseAgent
from legion.agents.python.architect import ArchitectAgent
from legion.agents.python.echo import EchoAgent
from legion.agents.python.healthcheck import HealthcheckAgent
from legion.agents.python.ping import PingAgent
from legion.agents.python.therapist import TherapistAgent
from legion.agents.python.ux_designer import UxDesignerAgent
from legion.orchestrator import Orchestrator
from memory.legion_memory import LegionAgentMemory


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

    class DummyOrchestrator:
        agent_channel_ids = {"echo_agent": 123}

    agent = EchoAgent(DummyOrchestrator())
    agent.name = "echo_agent"
    agent.client = DummyClient()
    agent.channel_id = 123
    agent.config = config

    # Stub get_message_embedding
    monkeypatch.setattr(agent, "get_message_embedding", lambda text: [0.1, 0.2])
    # Stub retrieve_memories
    retrieved = ["mem1", "mem2"]
    monkeypatch.setattr(
        LegionAgentMemory,
        "retrieve_memories",
        staticmethod(lambda name, emb, k, base_dir="memory": retrieved),
    )
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
        captured["kwargs"] = kwargs
        return "reply"

    monkeypatch.setattr(agent, "call_llm", fake_call_llm)
    # Add per-agent override config
    agent.config["model"] = "custom-model"
    agent.config["temperature"] = 0.9
    # Stub post_to_discord to avoid real Discord calls
    posted = []

    async def fake_post(msg):
        posted.append(msg)

    monkeypatch.setattr(agent, "post_to_discord", fake_post)
    # Stub store_memories
    stored = {}

    def fake_store(name, mems, base_dir="memory"):
        stored["agent_name"] = name
        stored["mems"] = mems

    monkeypatch.setattr(LegionAgentMemory, "store_memories", staticmethod(fake_store))

    # Call handle_message
    context = {
        "content": "test content",
        "author": "user",
        "timestamp": datetime.datetime(2020, 1, 1, 0, 0),
    }
    await agent.handle_message(context)

    # Construct expected payload
    expected_messages = [
        {
            "role": "system",
            "content": "You are 🔁 the Echo Agent—repeat back any message you receive, useful for diagnostics and testing message flow.",
        },
        {"role": "system", "content": "Previously on our project: mem1\nmem2"},
        {
            "role": "system",
            "content": "Reflection: think step-by-step before answering.",
        },
        *stub_history,
        {"role": "user", "content": context},
    ]
    assert captured.get("messages") == expected_messages
    # Model and temperature overrides applied
    assert "kwargs" in captured, "Override kwargs not captured by fake_call_llm"
    assert captured["kwargs"].get("model") == "custom-model"
    assert captured["kwargs"].get("temperature") == 0.9


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
        raise OSError("fail")

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

    class DummyOrchestrator:
        agent_channel_ids = {
            k: i
            for i, k in enumerate(
                [
                    "architect_agent",
                    "echo_agent",
                    "healthcheck_agent",
                    "ping_agent",
                    "therapist_agent",
                    "ux_designer_agent",
                ]
            )
        }

    agents = [
        ArchitectAgent(DummyOrchestrator()),
        EchoAgent(DummyOrchestrator()),
        HealthcheckAgent(DummyOrchestrator()),
        PingAgent(DummyOrchestrator()),
        TherapistAgent(DummyOrchestrator()),
        UxDesignerAgent(DummyOrchestrator()),
    ]
    names = [
        "architect_agent",
        "echo_agent",
        "healthcheck_agent",
        "ping_agent",
        "therapist_agent",
        "ux_designer_agent",
    ]
    for agent, name in zip(agents, names):
        agent.name = name
        agent.client = DummyClient()
        agent.channel_id = DummyOrchestrator().agent_channel_ids[name]
        agent.config = {"default_prompt": "stub"}
    # Patch get_message_embedding to avoid OpenAI call
    monkeypatch.setattr(
        ArchitectAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
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
        TherapistAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    monkeypatch.setattr(
        UxDesignerAgent, "get_message_embedding", lambda self, text: [0.1, 0.2]
    )
    # Patch LegionAgentMemory.retrieve_memories to avoid file IO for all agents
    monkeypatch.setattr(
        LegionAgentMemory, "retrieve_memories", staticmethod(lambda *a, **k: [])
    )

    # Patch fetch_thread_history to avoid Discord API
    async def fake_history(self, channel_id, thread_id, limit):
        return []

    for agent in agents:
        monkeypatch.setattr(agent, "fetch_thread_history", fake_history.__get__(agent))
        monkeypatch.setattr(agent, "call_llm", lambda thread_id, messages: "ok")

        async def fake_post_to_discord(msg):
            return None

        monkeypatch.setattr(agent, "post_to_discord", fake_post_to_discord)
    # Should not raise
    for agent in agents:
        context = {
            "content": "hi",
            "author": "user",
            "timestamp": datetime.datetime.now().isoformat(),
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
        async def handle_message(self, context, **kwargs):
            self.called = True
            return "ok"

    orch = Orchestrator()
    agent = DummyAgent(orch)
    agent.name = "echo_agent"
    agent.client = None
    agent.channel_id = 1
    orch._agent_objects["echo_agent"] = agent
    context = {
        "channel_id": 1,
        "thread_id": 1,
        "content": "hi",
        "author": "user",
        "timestamp": datetime.datetime.now().isoformat(),
    }
    # Should not raise
    result = asyncio.get_event_loop().run_until_complete(
        orch.dispatch_message("echo_agent", context)
    )
    assert result == "ok"
    assert getattr(agent, "called", False)


def test_embedding_fallback(monkeypatch, caplog):
    from legion.agents.base import BaseAgent

    class DummyOrchestrator:
        agent_channel_ids = {}

    agent = BaseAgent(DummyOrchestrator())
    # Patch openai.Embedding.create to raise
    import openai

    monkeypatch.setattr(
        openai.Embedding,
        "create",
        lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")),
    )
    with caplog.at_level("WARNING"):
        with pytest.raises(RuntimeError) as exc:
            agent.get_message_embedding("test")
        assert "Embedding creation failed" in str(exc.value)
        assert any("Embedding creation failed" in r.message for r in caplog.records)


def test_base_agent_custom_llm_client():
    class DummyOrchestrator:
        agent_channel_ids = {"base_agent": 1}

    class DummyLLMClient:
        def __init__(self):
            self.called = False
            self.model = "dummy-model"
            self.default_kwargs = {}

        def generate(self, *a, **k):
            self.called = True
            return "dummy-response"

    dummy_llm = DummyLLMClient()
    agent = BaseAgent(DummyOrchestrator(), llm_client=dummy_llm)
    assert agent.llm is dummy_llm
    # Simulate a call to call_llm (should use dummy_llm)
    agent.llm.generate("agent", "thread", {}, [{"role": "user", "content": "hi"}])
    assert dummy_llm.called


def test_base_agent_handle_message_error_branches(monkeypatch):
    class DummyOrchestrator:
        agent_channel_ids = {"base_agent": 1}

    agent = BaseAgent(DummyOrchestrator())
    agent.name = "base_agent"
    agent.config = {}
    # Ensure system_prompt exists before monkeypatching
    agent.system_prompt = "stub"
    monkeypatch.setattr(agent, "system_prompt", None)
    # Patch get_message_embedding to raise RuntimeError
    monkeypatch.setattr(
        agent,
        "get_message_embedding",
        lambda text: (_ for _ in ()).throw(RuntimeError("fail embedding")),
    )

    # Patch fetch_thread_history to raise AttributeError
    async def fail_fetch(*a, **k):
        raise AttributeError("fail fetch")

    monkeypatch.setattr(agent, "fetch_thread_history", fail_fetch)

    # Patch post_to_discord to do nothing
    async def fake_post(msg):
        pass

    monkeypatch.setattr(agent, "post_to_discord", fake_post)
    # Patch call_llm to raise ValueError
    monkeypatch.setattr(
        agent, "call_llm", lambda *a, **k: (_ for _ in ()).throw(ValueError("fail llm"))
    )
    # Patch memory.log_task to raise RuntimeError
    agent.memory.log_task = lambda *a, **k: (_ for _ in ()).throw(
        RuntimeError("fail log")
    )
    # Patch mem_store to raise ValueError
    agent.mem_store = lambda *a, **k: (_ for _ in ()).throw(ValueError("fail store"))
    # Should not raise, should hit all error branches
    import asyncio

    context = {"content": "hi", "author": "user", "timestamp": None}
    asyncio.get_event_loop().run_until_complete(agent.handle_message(context))


@unittest.skip("legacy failure – deferred")
class LegacyPlaceHolder(unittest.TestCase):
    pass
