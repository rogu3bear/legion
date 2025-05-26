"""Tests for prompt management API endpoints."""

import pytest
from unittest.mock import patch, mock_open
from fastapi.testclient import TestClient
from pathlib import Path

from interface.main import app
from interface.dependencies import get_current_active_user
from interface.models.user import User


# Mock user for testing
def mock_current_user():
    """Return a mock authenticated user."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        is_active=True,
        is_superuser=False,
        role="admin"
    )


@pytest.fixture
def test_client():
    """Create test client with mocked authentication."""
    app.dependency_overrides[get_current_active_user] = mock_current_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestPromptsAPI:
    """Test cases for prompts API endpoints."""

    def test_get_prompt_success(self, test_client):
        """Test successful prompt retrieval."""
        mock_content = "# Test Agent Prompt\nThis is a test prompt."

        with patch("interface.api.v1.endpoints.prompts.load_prompt", return_value=mock_content):
            response = test_client.get("/api/v1/prompts/test_agent")

        assert response.status_code == 200
        data = response.json()
        assert data["agent_name"] == "test_agent"
        assert data["content"] == mock_content

    def test_get_prompt_not_found(self, test_client):
        """Test prompt retrieval when file doesn't exist."""
        with patch("interface.api.v1.endpoints.prompts.load_prompt", return_value=None):
            response = test_client.get("/api/v1/prompts/nonexistent_agent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_prompt_success(self, test_client):
        """Test successful prompt update."""
        update_data = {"content": "# Updated Prompt\nThis is updated content."}

        with patch("interface.api.v1.endpoints.prompts.save_prompt", return_value=True):
            response = test_client.put("/api/v1/prompts/test_agent", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert "updated successfully" in data["message"]
        assert data["agent_name"] == "test_agent"

    def test_update_prompt_failure(self, test_client):
        """Test prompt update failure."""
        update_data = {"content": "# Updated Prompt\nThis is updated content."}

        with patch("interface.api.v1.endpoints.prompts.save_prompt", return_value=False):
            response = test_client.put("/api/v1/prompts/test_agent", json=update_data)

        assert response.status_code == 500
        assert "Failed to save" in response.json()["detail"]

    def test_create_prompt_success(self, test_client):
        """Test successful prompt creation."""
        create_data = {
            "agent_name": "new_agent",
            "content": "# New Agent Prompt\nThis is a new prompt."
        }

        with patch("interface.api.v1.endpoints.prompts.load_prompt", return_value=None), \
             patch("interface.api.v1.endpoints.prompts.save_prompt", return_value=True):
            response = test_client.post("/api/v1/prompts/", json=create_data)

        assert response.status_code == 201
        data = response.json()
        assert "created successfully" in data["message"]
        assert data["agent_name"] == "new_agent"

    def test_create_prompt_already_exists(self, test_client):
        """Test prompt creation when prompt already exists."""
        create_data = {
            "agent_name": "existing_agent",
            "content": "# Existing Agent Prompt"
        }

        with patch("interface.api.v1.endpoints.prompts.load_prompt", return_value="existing content"):
            response = test_client.post("/api/v1/prompts/", json=create_data)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_list_prompts(self, test_client):
        """Test listing all available prompts."""
        mock_agents = ["agent1", "agent2", "agent3"]

        with patch("interface.api.v1.endpoints.prompts.list_available_agents", return_value=mock_agents):
            response = test_client.get("/api/v1/prompts/")

        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert data["agents"] == mock_agents

    def test_get_all_prompts(self, test_client):
        """Test getting all prompts content."""
        mock_prompts = {
            "agent1": "# Agent 1 Prompt",
            "agent2": "# Agent 2 Prompt"
        }

        with patch("interface.api.v1.endpoints.prompts.get_all_prompts", return_value=mock_prompts):
            response = test_client.get("/api/v1/prompts/all")

        assert response.status_code == 200
        data = response.json()
        assert data == mock_prompts
