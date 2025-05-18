# This file is being renamed to test_middleware_chroma_client.py
# The content will be moved by a subsequent git mv command or IDE rename operation.
# For now, just adding a comment to signify the intent.
"""Tests for ChromaClient wrapper"""

import sys
import types

import pytest

from legion.core.utils.chroma_client import AsyncChromaClient as ChromaClient
from middleware.src.models import ChromaRecord

# Stub chromadb AsyncClient for test environment
sys.modules["chromadb"] = types.SimpleNamespace(
    AsyncClient=lambda api_url, api_key: None
)


@pytest.mark.asyncio
async def test_upsert_and_query(monkeypatch):
    # Setup dummy Chroma client
    async def dummy_get_or_create_collection(name):
        class Coll:
            async def upsert(self, docs):
                return True

        return Coll()

    cc = ChromaClient(api_url="http://test", api_key="key")
    cc.client = type(
        "C", (), {"get_or_create_collection": dummy_get_or_create_collection}
    )

    record = ChromaRecord(
        agent_name="test",
        interaction_id="1",
        role="user",
        tokens=123,
        embedding=[0.1, 0.2],
        timestamp="2025-01-01T00:00:00",
        tags=["tag1"],
    )
    await cc.upsert_batch([record])

    # similarity_search
    async def dummy_query(query_embeddings, n_results):
        return {
            "ids": ["test:1"],
            "metadatas": [record.dict()],
            "embeddings": [record.embedding],
        }

    monkeypatch.setattr(
        cc.client, "get_collection", lambda name: type("C", (), {"query": dummy_query})
    )
    res = await cc.query_similar("test", [0.1, 0.2], n_results=1)
    assert "ids" in res

    # delete_by_id
    async def dummy_delete(ids):
        return True

    monkeypatch.setattr(
        cc.client,
        "get_collection",
        lambda name: type("C", (), {"delete": dummy_delete}),
    )
    await cc.delete_by_id("test", "1")
