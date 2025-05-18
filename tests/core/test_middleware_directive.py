from unittest.mock import MagicMock, patch

import pytest

from legion.core.utils.sync_chroma_client import SyncChromaClient
from legion.core.middleware.directive_definitions import (AGENT_DIRECTIVE_STRING,
                                                        MIDDLEWARE_DIRECTIVE_PROMPT)
from legion.middleware.directive_compliance import DirectiveCompliance
from legion.middleware.request_middleware import (
    ACCEPTABLE_SIMILARITY,
    REVIEW_SIMILARITY,
    THERAPIST_AGENT_THRESHOLD,
    RequestMiddleware,
)


@pytest.fixture
def mock_chroma_client():
    client = MagicMock(spec=SyncChromaClient)
    client.create_embedding.return_value = [0.1, 0.2, 0.3]  # Dummy embedding
    return client


@pytest.fixture
def mock_directive_compliance():
    checker = MagicMock(spec=DirectiveCompliance)
    return checker


@pytest.fixture
def middleware(mock_chroma_client, mock_directive_compliance):
    return RequestMiddleware(
        chroma_client=mock_chroma_client, directive_checker=mock_directive_compliance
    )


# Embedding Validation Tests
def test_process_request_empty_text(middleware):
    status, details = middleware.process_request("", {})
    assert status == "rejected"
    assert details["reason"] == "Empty request text"
    assert details["source"] == "input_validation"


def test_process_request_embedding_creation_fails(middleware, mock_chroma_client):
    mock_chroma_client.create_embedding.side_effect = Exception("Chroma down")
    status, details = middleware.process_request("test", {})
    assert status == "rejected"
    assert "Failed to create embedding: Chroma down" in details["reason"]
    assert details["source"] == "embedding_system"


def test_process_request_retrieval_fails(middleware, mock_chroma_client):
    mock_chroma_client.retrieve_similar_embeddings.side_effect = Exception(
        "Retrieval error"
    )
    status, details = middleware.process_request("test", {})
    assert status == "rejected"
    assert "Failed to retrieve similar embeddings: Retrieval error" in details["reason"]
    assert details["source"] == "embedding_system"


def test_process_request_no_similar_embeddings(
    middleware, mock_chroma_client, mock_directive_compliance
):
    mock_chroma_client.retrieve_similar_embeddings.return_value = []
    mock_directive_compliance.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "needs_review"  # Default for no similar context
    assert details["reason"] == "No similar context found"
    assert details["source"] == "embedding_validation"


# Test for similarity below REVIEW_SIMILARITY (0.60) - should reject immediately
def test_process_request_similarity_rejected(middleware, mock_chroma_client):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": 0.50}
    ]  # Below REVIEW_SIMILARITY (0.60)
    # Directive checker won't be called if embedding similarity rejects directly
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "rejected"
    assert "below rejection threshold" in details["reason"]
    assert details["source"] == "embedding_validation"
    assert details["similarity"] == 0.50


# Test for similarity between REVIEW_SIMILARITY (0.60) and THERAPIST_AGENT_THRESHOLD (0.70) - should mark for review
def test_process_request_similarity_needs_review(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = (REVIEW_SIMILARITY + THERAPIST_AGENT_THRESHOLD) / 2  # e.g. 0.65
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]
    mock_directive_compliance.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "needs_review"
    assert "below therapist threshold" in details["reason"]
    assert details["source"] == "embedding_validation"


# Test for similarity between THERAPIST_AGENT_THRESHOLD (0.70) and ACCEPTABLE_SIMILARITY (0.85) - should escalate to therapist
def test_process_request_similarity_escalate_therapist(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = (THERAPIST_AGENT_THRESHOLD + ACCEPTABLE_SIMILARITY) / 2  # e.g. 0.775
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]
    mock_directive_compliance.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "escalated_therapist"
    assert "below acceptable threshold" in details["reason"]
    assert details["source"] == "embedding_validation"


# Test for similarity above ACCEPTABLE_SIMILARITY (0.85) - should approve
def test_process_request_similarity_acceptable(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = ACCEPTABLE_SIMILARITY + 0.05  # e.g. 0.90
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]
    mock_directive_compliance.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "approved"
    assert "meets acceptable threshold" in details["reason"]
    assert details["source"] == "combined_approval"


# Directive Compliance Tests (Integrated with Middleware)
def test_process_request_directive_non_compliant(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = ACCEPTABLE_SIMILARITY + 0.05  # e.g. 0.90
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]  # Embedding OK
    mock_directive_compliance.check.return_value = (
        "non_compliant",
        {"reason": "bad keyword"},
    )
    status, details = middleware.process_request(
        "test with bad_keyword", {"agent_id": "test_agent"}
    )
    assert status == "rejected"
    assert details["reason"] == "bad keyword"
    assert details["source"] == "directive_compliance"


def test_process_request_directive_therapist_triggered(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = ACCEPTABLE_SIMILARITY + 0.05  # e.g. 0.90
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]  # Embedding OK
    mock_directive_compliance.check.return_value = (
        "therapist_triggered",
        {"reason": "critical issue"},
    )
    status, details = middleware.process_request(
        "critical request", {"agent_id": "test_agent"}
    )
    assert status == "escalated_therapist"
    assert details["reason"] == "critical issue"
    assert details["source"] == "directive_compliance"


# Test directive rejection taking precedence over embedding acceptance
def test_process_request_directive_rejection_takes_precedence(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = ACCEPTABLE_SIMILARITY + 0.05  # e.g. 0.90
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]  # Embedding would otherwise be approved
    mock_directive_compliance.check.return_value = (
        "non_compliant",
        {"reason": "directive violation"},
    )
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "rejected"
    assert details["reason"] == "directive violation"
    assert details["source"] == "directive_compliance"


# Test directive therapist escalation taking precedence over embedding acceptance
def test_process_request_directive_therapist_takes_precedence(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = ACCEPTABLE_SIMILARITY + 0.05  # e.g. 0.90
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]  # Embedding would otherwise be approved
    mock_directive_compliance.check.return_value = (
        "therapist_triggered",
        {"reason": "suspicious pattern"},
    )
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "escalated_therapist"
    assert details["reason"] == "suspicious pattern"
    assert details["source"] == "directive_compliance"


# Test directive therapist escalation taking precedence over embedding needs_review
def test_process_request_directive_therapist_takes_precedence_over_embedding_review(
    middleware, mock_chroma_client, mock_directive_compliance
):
    similarity = (REVIEW_SIMILARITY + THERAPIST_AGENT_THRESHOLD) / 2  # e.g. 0.65
    mock_chroma_client.retrieve_similar_embeddings.return_value = [
        {"id": "doc1", "similarity": similarity}
    ]  # Embedding would otherwise be needs_review
    mock_directive_compliance.check.return_value = (
        "therapist_triggered",
        {"reason": "suspicious pattern"},
    )
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "escalated_therapist"
    assert details["reason"] == "suspicious pattern"
    assert details["source"] == "directive_compliance"
