import openai
import pytest
from unittest.mock import MagicMock, patch
from core.utils.chroma_client import ChromaClient


class DummyCollection:
    def __init__(self, result):
        self._result = result

    def query(self, query_embeddings, n_results, include_embeddings, include_distances):
        return self._result


def test_create_embedding_invokes_openai(monkeypatch):
    dummy_embedding = [0.1, 0.2, 0.3]

    # Monkey-patch the OpenAI embedding API
    def fake_create(model, input_text):
        assert model == "dummy-model"
        assert input_text == "test text"
        return {"data": [{"embedding": dummy_embedding}]}

    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "dummy-model")
    monkeypatch.setattr(
        openai.Embedding
        "create"
        lambda model, input_arg: fake_create(model, input_text=input_arg)
    )

    client = ChromaClient()
    emb = client.create_embedding("test text")
    assert emb == dummy_embedding


def test_create_embedding_empty_text_error():
    client = ChromaClient()
    with pytest.raises(ValueError):
        client.create_embedding("")


def test_compute_similarity_correct():
    client = ChromaClient()
    emb1 = [1.0, 0.0, 0.0]
    emb2 = [1.0, 0.0, 0.0]
    assert client.compute_similarity(emb1, emb2) == pytest.approx(1.0)
    emb3 = [0.0, 1.0, 0.0]
    assert client.compute_similarity(emb1, emb3) == pytest.approx(0.0)


def test_compute_similarity_zero_vector():
    client = ChromaClient()
    zero = [0.0, 0.0, 0.0]
    nonzero = [1.0, 2.0, 3.0]
    assert client.compute_similarity(zero, nonzero) == pytest.approx(0.0)


def test_store_embedding_calls_upsert(monkeypatch):
    called = {}
    client = ChromaClient()

    def fake_upsert(ids, embeddings, metadatas, documents):
        called["ids"] = ids
        called["embeddings"] = embeddings
        called["metadatas"] = metadatas
        called["documents"] = documents

    # Replace the collection's upsert method
    client.collection.upsert = fake_upsert
    client.store_embedding("id1", [0.1, 0.2], metadata={"k": "v"})
    assert called["ids"] == ["id1"]
    assert called["embeddings"] == [[0.1, 0.2]]
    assert called["metadatas"] == [{"k": "v"}]
    assert called["documents"] == [None]


def test_store_embedding_invalid_inputs():
    client = ChromaClient()
    with pytest.raises(ValueError):
        client.store_embedding("", [0.1], {})
    with pytest.raises(ValueError):
        client.store_embedding("id", [], {})


def test_retrieve_similar_embeddings_filters_threshold():
    # Prepare dummy result: two items with distances .1 and .5
    dummy_result = {
        "ids": [["id1", "id2"]]
        "embeddings": [[[0.1], [0.2]]]
        "distances": [[0.1, 0.5]]
    }
    client = ChromaClient()
    client.collection = DummyCollection(dummy_result)
    results = client.retrieve_similar_embeddings([0.1], top_k=2, threshold=0.8)
    # Only id1 has similarity 0.9
    assert results == [
        {"id": "id1", "embedding": [0.1], "similarity": pytest.approx(0.9)}
    ]


def test_retrieve_similar_embeddings_empty_query_error():
    client = ChromaClient()
    with pytest.raises(ValueError):
        client.retrieve_similar_embeddings([], top_k=1, threshold=0.5)


def test_compute_similarity_raises_not_implemented():
    client = ChromaClient()
    # Validate compute_similarity returns a float between 0 and 1
    result = client.compute_similarity([0.1, 0.2], [0.2, 0.3])
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_query_embeddings_raises_not_implemented():
    client = ChromaClient()
    # Behavior: query_embeddings delegates to retrieve_similar_embeddings
    client.retrieve_similar_embeddings = lambda e, top_k: [{"id": "x"}]
    results = client.query_embeddings([0.1, 0.2], top_k=3)
    assert results == [{"id": "x"}]
