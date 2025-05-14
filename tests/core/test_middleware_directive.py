import pytest
from unittest.mock import MagicMock, patch
from core.middleware.middleware import RequestMiddleware
from core.middleware.directive_compliance import DirectiveCompliance
from core.utils.chroma_client import ChromaClient

@pytest.fixture
def mock_chroma_client():
    client = MagicMock(spec=ChromaClient)
    client.create_embedding.return_value = [0.1, 0.2, 0.3] # Dummy embedding
    return client

@pytest.fixture
def mock_directive_compliance():
    checker = MagicMock(spec=DirectiveCompliance)
    return checker

@pytest.fixture
def middleware(mock_chroma_client, mock_directive_compliance):
    return RequestMiddleware(chroma_client=mock_chroma_client, directive_checker=mock_directive_compliance)

# Embedding Validation Tests
def test_process_request_empty_text(middleware):
    status, details = middleware.process_request("", {})
    assert status == "rejected"
    assert details["reason"] == "Empty request text"

def test_process_request_embedding_creation_fails(middleware, mock_chroma_client):
    mock_chroma_client.create_embedding.side_effect = Exception("Chroma down")
    status, details = middleware.process_request("test", {})
    assert status == "rejected"
    assert "Failed to create embedding: Chroma down" in details["reason"]

def test_process_request_retrieval_fails(middleware, mock_chroma_client):
    mock_chroma_client.retrieve_similar_embeddings.side_effect = Exception("Retrieval error")
    status, details = middleware.process_request("test", {})
    assert status == "rejected"
    assert "Failed to retrieve similar embeddings: Retrieval error" in details["reason"]

def test_process_request_no_similar_embeddings(middleware, mock_chroma_client):
    mock_chroma_client.retrieve_similar_embeddings.return_value = []
    middleware.directive_checker.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "needs_review" # Default for no similar context
    assert details["embedding_reason"] == "No similar context found."

def test_process_request_similarity_acceptable(middleware, mock_chroma_client):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.90}]
    middleware.directive_checker.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "approved"
    assert details["top_similarity"] == 0.90

def test_process_request_similarity_needs_review(middleware, mock_chroma_client):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.80}] # Between 0.60 and 0.85
    middleware.directive_checker.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "needs_review"
    assert "below acceptable threshold" in details["embedding_reason"]

def test_process_request_similarity_rejected(middleware, mock_chroma_client):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.50}] # Below 0.60
    # Directive checker won't be called if embedding similarity rejects directly
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "rejected"
    assert "below rejection threshold" in details["embedding_reason"]

def test_process_request_similarity_triggers_therapist(middleware, mock_chroma_client):
    # Similarity is e.g. 0.65 (needs_review range but also < THERAPIST_AGENT_THRESHOLD 0.70)
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.65}]
    middleware.directive_checker.check.return_value = ("compliant", {})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "escalated_therapist"
    assert "below therapist threshold" in details["embedding_reason"]

# Directive Compliance Tests (Integrated with Middleware)
def test_process_request_directive_non_compliant(middleware, mock_chroma_client, mock_directive_compliance):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.90}] # Embedding OK
    mock_directive_compliance.check.return_value = ("non_compliant", {"reason": "bad keyword"})
    status, details = middleware.process_request("test with bad_keyword", {"agent_id": "test_agent"})
    assert status == "non_compliant"
    assert details["reason"] == "bad keyword"
    assert details["source"] == "directive_compliance"

def test_process_request_directive_therapist_triggered(middleware, mock_chroma_client, mock_directive_compliance):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.90}] # Embedding OK
    mock_directive_compliance.check.return_value = ("therapist_triggered", {"reason": "critical issue"})
    status, details = middleware.process_request("critical request", {"agent_id": "test_agent"})
    assert status == "therapist_triggered"
    assert details["reason"] == "critical issue"
    assert details["source"] == "directive_compliance"

def test_process_request_embedding_review_directive_compliant(middleware, mock_chroma_client, mock_directive_compliance):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.80}] # Embedding needs review
    mock_directive_compliance.check.return_value = ("compliant", {"checks_passed": ["all good"]})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "needs_review" # Embedding status should prevail if stronger
    assert "below acceptable threshold" in details["embedding_reason"]
    assert details["source"] == "embedding_validation"

def test_process_request_embedding_therapist_directive_compliant(middleware, mock_chroma_client, mock_directive_compliance):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.65}] # Embedding triggers therapist
    mock_directive_compliance.check.return_value = ("compliant", {"checks_passed": ["all good"]})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "escalated_therapist" # Embedding therapist trigger prevails
    assert "below therapist threshold" in details["embedding_reason"]
    assert details["source"] == "embedding_validation"

def test_process_request_embedding_approved_directive_non_compliant_overrides(middleware, mock_chroma_client, mock_directive_compliance):
    mock_chroma_client.retrieve_similar_embeddings.return_value = [{"id": "doc1", "similarity": 0.90}] # Embedding approved
    mock_directive_compliance.check.return_value = ("non_compliant", {"reason": "directive fail", "checks_failed":["failed directive check"]})
    status, details = middleware.process_request("test", {"agent_id": "test_agent"})
    assert status == "non_compliant"
    assert details["reason"] == "directive fail"
    assert details["source"] == "directive_compliance"

def test_directive_compliance_stub():
    # TODO: implement directive compliance enforcement tests.
    pass 