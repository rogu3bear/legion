from legion.core.indexing import build_inverted_index
from legion.core.network import basic_health_check
from skills.search import vector_search
from skills.summarize import summarize_snippets


def test_vector_search_basic():
    docs = [
        {"text": "foo", "embedding": [1, 0]},
        {"text": "bar", "embedding": [0, 1]},
        {"text": "baz", "embedding": [0.7, 0.7]},
    ]
    query = [1, 0]
    out = vector_search(query, docs, top_k=2)
    assert out[0]["text"] == "foo"
    assert len(out) == 2


def test_build_inverted_index():
    docs = [
        {"text": "Hello world"},
        {"text": "world of code"},
        {"text": "hello again"},
    ]
    idx = build_inverted_index(docs)
    assert "hello" in idx and 0 in idx["hello"] and 2 in idx["hello"]
    assert "world" in idx and 0 in idx["world"] and 1 in idx["world"]


def test_basic_health_check(monkeypatch):
    class DummyResp:
        def __init__(self, code):
            self.status_code = code

    def fake_get(url, timeout):
        return DummyResp(200)

    monkeypatch.setattr("requests.get", fake_get)
    out = basic_health_check("http://test/", timeout=0.1)
    assert out["ok"] is True
    assert out["status"] == 200
    assert "elapsed" in out


def test_summarize_snippets(monkeypatch):
    # Patch openai.ChatCompletion.create
    class DummyResp:
        class Choice:
            def __init__(self, content):
                self.message = type("msg", (), {"content": content})

        def __init__(self, content):
            self.choices = [self.Choice(content)]

    def fake_create(**kwargs):
        return DummyResp("summary")

    import openai

    monkeypatch.setattr(openai.ChatCompletion, "create", fake_create)
    snippets = ["foo", "bar"]
    out = summarize_snippets(snippets, model="gpt-3.5-turbo", max_tokens=32)
    assert out == "summary"

    # Test error path
    def fail_create(**kwargs):
        raise Exception("fail")

    monkeypatch.setattr(openai.ChatCompletion, "create", fail_create)
    out2 = summarize_snippets(snippets)
    assert out2.startswith("[Summarization error:")
