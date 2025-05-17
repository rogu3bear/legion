from legion.orchestrator.tag_middleware import tag_payload, CORE_TAG


def dummy(payload):
    return payload


def test_tag_payload_decorator():
    decorated = tag_payload(["test"])(dummy)
    result = decorated({"message": "hi"})
    assert result["tags"] == [CORE_TAG, "test"]
