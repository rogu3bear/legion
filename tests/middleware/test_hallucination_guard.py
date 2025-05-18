import pytest
from legion.middleware.hallucination_guard import guard_response


def test_guard_response_valid(mocker):
    mock_post = mocker.patch("legion.middleware.hallucination_guard.post_agent_feed")
    result = guard_response({"confidence": 0.9}, threshold=0.8)
    assert result["valid"]
    assert result["response"]["confidence"] == 0.9
    mock_post.assert_not_called()


def test_guard_response_invalid(mocker):
    mock_post = mocker.patch("legion.middleware.hallucination_guard.post_agent_feed")
    result = guard_response({"confidence": 0.5}, threshold=0.8)
    assert not result["valid"]
    assert "Low confidence" in result["reason"]
    mock_post.assert_called_once()


def test_guard_response_no_confidence(mocker):
    mock_post = mocker.patch("legion.middleware.hallucination_guard.post_agent_feed")
    result = guard_response({}, threshold=0.8)
    assert not result["valid"]
    mock_post.assert_called_once()
