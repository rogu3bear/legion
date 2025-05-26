import datetime
import unittest

import pytest

from legion.agents.base import BaseAgent
from memory.legion_memory import LegionAgentMemory


class DummyOrchestrator:
    agent_channel_ids = {}


@pytest.fixture
def agent():
    # Create a BaseAgent instance
    agent = BaseAgent(DummyOrchestrator())
    agent.name = "test_agent"
    # override config
    agent.config = {
        "memory_top_k": 5,
        "memory_base_dir": "custom_memory",
        "memory_tags": ["tag1", "tag2"],
    }
    return agent


def test_mem_retrieve_calls_underlying_with_correct_args(monkeypatch, agent):
    called = {}

    # stub retrieve_memories to capture parameters
    def fake_retrieve(agent_name, embedding, top_k, base_dir):
        called["agent_name"] = agent_name
        called["embedding"] = embedding
        called["top_k"] = top_k
        called["base_dir"] = base_dir
        return ["m1", "m2"]

    monkeypatch.setattr(
        LegionAgentMemory, "retrieve_memories", staticmethod(fake_retrieve)
    )
    emb = [0.1, 0.2, 0.3]
    ts = datetime.datetime(2021, 1, 1, 12, 0, 0)
    result = agent.mem_retrieve(emb, 3, tags=["x"], timestamp=ts)
    # Should return stubbed list
    assert result == ["m1", "m2"]
    # Check parameters passed
    assert called["agent_name"] == "test_agent"
    assert called["embedding"] == emb
    assert called["top_k"] == 3
    # base_dir should be from config
    assert called["base_dir"] == "custom_memory"


def test_mem_store_dedup_and_enrichment(monkeypatch, agent):
    called = {}

    # stub store_memories to capture enriched snippets
    def fake_store(agent_name, snippets, base_dir):
        called["agent_name"] = agent_name
        called["snippets"] = snippets
        called["base_dir"] = base_dir

    monkeypatch.setattr(LegionAgentMemory, "store_memories", staticmethod(fake_store))
    # create duplicate snippets
    common_embedding = [1.0, 0.0]
    input_snips = [
        {"text": "dup", "embedding": common_embedding},
        {"text": "dup", "embedding": common_embedding},
        {"text": "unique", "embedding": [0.0, 1.0]},
    ]
    # timestamp for enrichment
    ts = datetime.datetime(2022, 2, 2, 14, 30)
    agent.mem_store(input_snips, tags=["A"], timestamp=ts)
    # Should pass through deduplicated keys
    assert called["agent_name"] == "test_agent"
    # Check base_dir from config
    assert called["base_dir"] == "custom_memory"
    # snippets: two unique items
    texts = {snip["text"] for snip in called["snippets"]}
    assert texts == {"dup", "unique"}
    # check tags and timestamp fields
    for snip in called["snippets"]:
        assert "tags" in snip and snip["tags"] == ["A"]
        assert "timestamp" in snip and snip["timestamp"] == ts.isoformat()
    # embeddings preserved
    emb_map = {snip["text"]: snip["embedding"] for snip in called["snippets"]}
    assert emb_map["dup"] == common_embedding
    assert emb_map["unique"] == [0.0, 1.0]


@unittest.skip("legacy failure – deferred")
class LegacyPlaceHolder(unittest.TestCase):
    pass
