"""Tests for Legion Web Interface API endpoints."""

import uuid
from unittest.mock import patch  # Added for mocking

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Core Imports
from interface.core.config import settings

# Security Imports
from interface.core.security import get_password_hash  # Import password hasher

# DB Imports
from interface.db.base import Base  # Import Base
from interface.db.session import (
    TestingSessionLocal,
    engine,
)  # Import engine and session factory
from interface.main import app

# Model Imports
from interface.models.user import (
    User as UserModel,
)  # Rename to avoid confusion with schema


@pytest.fixture(scope="module")
def client():
    # Use context manager to trigger startup and shutdown events
    with TestClient(app) as client:
        yield client


# Helper function for unique user data
def unique_user_data(prefix: str) -> dict:
    """Generates unique user data for tests."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"{prefix}_user_{unique_id}",
        "email": f"{prefix}_{unique_id}@example.com",
        "password": f"password_{unique_id}",
    }


# --- Auth Endpoints ---
def test_register_user(client: TestClient):
    """Ensure a user can register successfully."""
    user_data = unique_user_data("register")

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    created = response.json()
    assert created["username"] == user_data["username"]
    assert created["email"] == user_data["email"]
    assert "id" in created


def test_login_user_success(client: TestClient):
    """Test successful user login and token retrieval."""
    user_data = unique_user_data("login_success")
    # 1. Register user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    # 2. Login with correct credentials
    login_payload = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_response = client.post("/api/v1/login/access-token", data=login_payload)
    assert login_response.status_code == 200, login_response.text
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_user_incorrect_password(client: TestClient):
    """Test login attempt with incorrect password."""
    user_data = unique_user_data("login_fail_pass")
    # 1. Register user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    # 2. Attempt login with wrong password
    login_payload = {"username": user_data["username"], "password": "wrongpassword"}
    login_response = client.post("/api/v1/login/access-token", data=login_payload)
    assert login_response.status_code == 401
    assert "Incorrect username or password" in login_response.text


def test_login_user_nonexistent_username(client: TestClient):
    """Test login attempt with a username that does not exist."""
    login_payload = {"username": "nonexistentuser", "password": "anypassword"}
    login_response = client.post("/api/v1/login/access-token", data=login_payload)
    assert login_response.status_code == 401
    assert "Incorrect username or password" in login_response.text


def test_me_endpoint_unauthenticated(client: TestClient):
    """Test accessing /me endpoint without authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401  # Or 403 depending on setup
    assert "Not authenticated" in response.text  # Check for expected detail


def test_me_endpoint_authenticated(client: TestClient):
    """Test accessing /me endpoint with valid authentication."""
    user_data = unique_user_data("me_auth")
    # 1. Register user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    # 2. Login to get token
    login_payload = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_response = client.post("/api/v1/login/access-token", data=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Access /me with token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200, me_response.text
    me_data = me_response.json()
    assert me_data["username"] == user_data["username"]
    assert me_data["email"] == user_data["email"]
    assert "hashed_password" not in me_data


# --- Test Fixtures --- START ---


# Fixture to create a regular user and return their token
@pytest.fixture(scope="function")
def regular_user_token_headers(
    client: TestClient, db_session: Session
) -> dict[str, str]:
    user_data = unique_user_data("regular")
    # Use db_session to create user directly for fixture isolation
    hashed_password = get_password_hash(user_data["password"])
    db_user = UserModel(
        username=user_data["username"],
        email=user_data["email"],
        password_hash=hashed_password,
        is_active=True,
        is_superuser=False,  # Ensure it's a regular user
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    login_payload = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_response = client.post("/api/v1/login/access-token", data=login_payload)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Fixture to create a superuser and return their token
@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    # Create user directly in DB as superuser (or adapt registration if role/superuser flag is added)
    username = "superuser_test"
    email = "superuser@example.com"
    password = "superpassword"
    hashed_password = get_password_hash(password)
    db_user = UserModel(
        username=username,
        email=email,
        password_hash=hashed_password,
        is_active=True,
        is_superuser=True,  # Mark as superuser
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    login_payload = {"username": username, "password": password}
    login_response = client.post("/api/v1/login/access-token", data=login_payload)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Fixture for the database session (replaces override_get_db for cleaner test functions)
@pytest.fixture(scope="session")  # Use session scope for efficiency
def db_session():
    Base.metadata.drop_all(bind=engine)  # Ensure clean slate for session
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Clean up after session


# --- Agent Endpoints --- START ---
def test_list_agents_unauthenticated(client: TestClient):  # Add client fixture
    """Test accessing /agents endpoint without authentication."""
    response = client.get("/api/v1/agents/")
    assert response.status_code == 401  # Depends on reusable_oauth2 setup
    assert "Not authenticated" in response.text


def test_list_agents_authenticated(
    client: TestClient, regular_user_token_headers: dict
):
    """Test accessing /agents endpoint with valid regular user authentication."""
    response = client.get("/api/v1/agents/", headers=regular_user_token_headers)
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_create_agent_by_superuser(client: TestClient, superuser_token_headers: dict):
    """Test creating an agent as a superuser."""
    agent_data = {"name": "TestAgent1", "model": "test-model"}
    response = client.post(
        "/api/v1/agents/", headers=superuser_token_headers, json=agent_data
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == agent_data["name"]
    assert data["model"] == agent_data["model"]
    assert "id" in data


def test_create_agent_by_regular_user(
    client: TestClient, regular_user_token_headers: dict
):
    """Test creating an agent fails for a regular user."""
    agent_data = {"name": "TestAgent2", "model": "test-model"}
    response = client.post(
        "/api/v1/agents/", headers=regular_user_token_headers, json=agent_data
    )
    assert (
        response.status_code == 400
    )  # Or 403 depending on how superuser dep handles it
    assert "enough privileges" in response.text


def test_read_agent_by_regular_user(
    client: TestClient, superuser_token_headers: dict, regular_user_token_headers: dict
):
    """Test reading a specific agent as a regular user."""
    # 1. Create agent as superuser
    agent_data = {"name": "ReadableAgent", "model": "read-model"}
    create_response = client.post(
        "/api/v1/agents/", headers=superuser_token_headers, json=agent_data
    )
    assert create_response.status_code == 201
    agent_id = create_response.json()["id"]

    # 2. Read agent as regular user
    response = client.get(
        f"/api/v1/agents/{agent_id}", headers=regular_user_token_headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == agent_data["name"]


def test_read_nonexistent_agent(client: TestClient, regular_user_token_headers: dict):
    """Test reading a non-existent agent returns 404."""
    response = client.get("/api/v1/agents/9999", headers=regular_user_token_headers)
    assert response.status_code == 404
    assert "Agent not found" in response.text


def test_update_agent_by_superuser(client: TestClient, superuser_token_headers: dict):
    """Test updating an agent as a superuser."""
    # Create agent
    agent_data = {"name": "UpdateAgent", "model": "update-model"}
    create_response = client.post(
        "/api/v1/agents/", headers=superuser_token_headers, json=agent_data
    )
    assert create_response.status_code == 201
    agent_id = create_response.json()["id"]
    # Update agent
    update_data = {"description": "Updated description", "temperature": 0.9}
    update_response = client.put(
        f"/api/v1/agents/{agent_id}", headers=superuser_token_headers, json=update_data
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["description"] == "Updated description"
    assert updated["temperature"] == 0.9


def test_update_agent_by_regular_user_forbidden(
    client: TestClient, regular_user_token_headers: dict, superuser_token_headers: dict
):
    """Test updating an agent as a regular user is forbidden."""
    # Create agent as superuser
    agent_data = {"name": "NoUpdateAgent", "model": "no-update-model"}
    create_response = client.post(
        "/api/v1/agents/", headers=superuser_token_headers, json=agent_data
    )
    assert create_response.status_code == 201
    agent_id = create_response.json()["id"]
    # Attempt update as regular user
    update_data = {"description": "Should not update"}
    update_response = client.put(
        f"/api/v1/agents/{agent_id}",
        headers=regular_user_token_headers,
        json=update_data,
    )
    assert update_response.status_code == 400 or update_response.status_code == 403
    assert "enough privileges" in update_response.text


def test_update_nonexistent_agent(client: TestClient, superuser_token_headers: dict):
    """Test updating a non-existent agent returns 404."""
    update_data = {"description": "Does not exist"}
    response = client.put(
        "/api/v1/agents/9999", headers=superuser_token_headers, json=update_data
    )
    assert response.status_code == 404
    assert "Agent not found" in response.text


def test_update_agent_name_conflict(client: TestClient, superuser_token_headers: dict):
    """Test updating an agent to a name that already exists returns 400."""
    # Create two agents
    agent1 = {"name": "AgentA", "model": "model-a"}
    agent2 = {"name": "AgentB", "model": "model-b"}
    client.post("/api/v1/agents/", headers=superuser_token_headers, json=agent1)
    resp2 = client.post("/api/v1/agents/", headers=superuser_token_headers, json=agent2)
    id2 = resp2.json()["id"]
    # Attempt to update AgentB's name to AgentA
    update_data = {"name": "AgentA"}
    response = client.put(
        f"/api/v1/agents/{id2}", headers=superuser_token_headers, json=update_data
    )
    assert response.status_code == 400
    assert "Agent name already exists" in response.text


def test_delete_agent_by_superuser(client: TestClient, superuser_token_headers: dict):
    """Test deleting an agent as a superuser."""
    # Create agent
    agent_data = {"name": "DeleteAgent", "model": "delete-model"}
    create_response = client.post(
        "/api/v1/agents/", headers=superuser_token_headers, json=agent_data
    )
    assert create_response.status_code == 201
    agent_id = create_response.json()["id"]
    # Delete agent
    delete_response = client.delete(
        f"/api/v1/agents/{agent_id}", headers=superuser_token_headers
    )
    assert delete_response.status_code == 200
    deleted = delete_response.json()
    assert deleted["id"] == agent_id
    # Confirm agent is gone
    get_response = client.get(
        f"/api/v1/agents/{agent_id}", headers=superuser_token_headers
    )
    assert get_response.status_code == 404


def test_delete_agent_by_regular_user_forbidden(
    client: TestClient, regular_user_token_headers: dict, superuser_token_headers: dict
):
    """Test deleting an agent as a regular user is forbidden."""
    # Create agent as superuser
    agent_data = {"name": "NoDeleteAgent", "model": "no-delete-model"}
    create_response = client.post(
        "/api/v1/agents/", headers=superuser_token_headers, json=agent_data
    )
    assert create_response.status_code == 201
    agent_id = create_response.json()["id"]
    # Attempt delete as regular user
    delete_response = client.delete(
        f"/api/v1/agents/{agent_id}", headers=regular_user_token_headers
    )
    assert delete_response.status_code == 400 or delete_response.status_code == 403
    assert "enough privileges" in delete_response.text


def test_delete_nonexistent_agent(client: TestClient, superuser_token_headers: dict):
    """Test deleting a non-existent agent returns 404."""
    response = client.delete("/api/v1/agents/9999", headers=superuser_token_headers)
    assert response.status_code == 404
    assert "Agent not found" in response.text


# --- Agent Endpoints --- END ---

# --- System Endpoints --- START ---


# Mock orchestrator_comm functions for system endpoint tests
@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_orchestrator_status_success(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test successfully getting orchestrator status via IPC."""
    mock_command_id = "cmd-test-success"
    mock_send.return_value = mock_command_id
    mock_response = {
        "command_id": mock_command_id,
        "response": {
            "status": "ok",
            "detail": "Orchestrator is running",
            "pid": 12345,
            "active_agents": ["architect_agent", "metrics_agent"],
        },
    }
    mock_await.return_value = mock_response

    response = client.get(
        "/api/v1/system/status/orchestrator", headers=regular_user_token_headers
    )

    assert response.status_code == 200
    assert response.json() == mock_response["response"]
    mock_send.assert_called_once_with({"action": "status"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_orchestrator_status_timeout(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test timeout scenario when waiting for orchestrator response."""
    mock_command_id = "cmd-test-timeout"
    mock_send.return_value = mock_command_id
    mock_await.return_value = None  # Simulate timeout

    response = client.get(
        "/api/v1/system/status/orchestrator", headers=regular_user_token_headers
    )

    assert response.status_code == 504
    assert "No response received from orchestrator" in response.text
    mock_send.assert_called_once_with({"action": "status"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_orchestrator_status_error_response(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test scenario where orchestrator returns an error status."""
    mock_command_id = "cmd-test-error"
    mock_send.return_value = mock_command_id
    mock_response = {
        "command_id": mock_command_id,
        "response": {"status": "error", "detail": "Something went wrong"},
    }
    mock_await.return_value = mock_response

    response = client.get(
        "/api/v1/system/status/orchestrator", headers=regular_user_token_headers
    )

    assert response.status_code == 500
    assert "Orchestrator returned an error: Something went wrong" in response.text
    mock_send.assert_called_once_with({"action": "status"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


@patch("interface.api.v1.endpoints.system.send_command")
def test_get_orchestrator_status_send_error(
    mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test scenario where sending the command via IPC fails."""
    mock_send.side_effect = OSError("Disk full")

    response = client.get(
        "/api/v1/system/status/orchestrator", headers=regular_user_token_headers
    )

    assert response.status_code == 503
    assert "Failed to send command to orchestrator" in response.text
    mock_send.assert_called_once_with({"action": "status"})


def test_get_orchestrator_status_unauthenticated(client: TestClient):
    """Test accessing orchestrator status endpoint without authentication."""
    response = client.get("/api/v1/system/status/orchestrator")
    assert response.status_code == 401
    assert "Not authenticated" in response.text


@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_system_metrics_success(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test successfully getting system metrics via IPC."""
    mock_command_id = "cmd-metrics-success"
    mock_send.return_value = mock_command_id
    mock_response = {
        "command_id": mock_command_id,
        "response": {"status": "ok", "metrics": {"cpu": 10.1, "mem": 512}},
    }
    mock_await.return_value = mock_response

    response = client.get("/api/v1/system/metrics", headers=regular_user_token_headers)

    assert response.status_code == 200
    assert response.json() == mock_response["response"]
    mock_send.assert_called_once_with({"action": "metrics"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_system_metrics_timeout(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test timeout scenario for system metrics request."""
    mock_command_id = "cmd-metrics-timeout"
    mock_send.return_value = mock_command_id
    mock_await.return_value = None  # Simulate timeout

    response = client.get("/api/v1/system/metrics", headers=regular_user_token_headers)

    assert response.status_code == 504
    assert "No response received from orchestrator for metrics" in response.text
    mock_send.assert_called_once_with({"action": "metrics"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


def test_get_system_metrics_unauthenticated(client: TestClient):
    """Test accessing system metrics endpoint without authentication."""
    response = client.get("/api/v1/system/metrics")
    assert response.status_code == 401
    assert "Not authenticated" in response.text


@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_system_logs_success(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test successfully retrieving system logs via IPC."""
    mock_command_id = "cmd-logs-success"
    mock_send.return_value = mock_command_id
    mock_response = {
        "command_id": mock_command_id,
        "response": {
            "status": "ok",
            "logs": [
                {
                    "timestamp": "2024-06-01T12:00:00Z",
                    "level": "INFO",
                    "msg": "System started",
                },
                {
                    "timestamp": "2024-06-01T12:01:00Z",
                    "level": "ERROR",
                    "msg": "Agent crashed",
                },
            ],
        },
    }
    mock_await.return_value = mock_response

    response = client.get("/api/v1/system/logs", headers=regular_user_token_headers)

    assert response.status_code == 200
    assert response.json() == mock_response["response"]
    mock_send.assert_called_once_with({"action": "logs"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_system_logs_timeout(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test timeout scenario when waiting for system logs response."""
    mock_command_id = "cmd-logs-timeout"
    mock_send.return_value = mock_command_id
    mock_await.return_value = None  # Simulate timeout

    response = client.get("/api/v1/system/logs", headers=regular_user_token_headers)

    assert response.status_code == 504
    assert "No response received from orchestrator for logs" in response.text
    mock_send.assert_called_once_with({"action": "logs"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


@patch("interface.api.v1.endpoints.system.send_command")
@patch("interface.api.v1.endpoints.system.await_response")
def test_get_system_logs_error_response(
    mock_await, mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test scenario where orchestrator returns an error for logs."""
    mock_command_id = "cmd-logs-error"
    mock_send.return_value = mock_command_id
    mock_response = {
        "command_id": mock_command_id,
        "response": {"status": "error", "detail": "Log retrieval failed"},
    }
    mock_await.return_value = mock_response

    response = client.get("/api/v1/system/logs", headers=regular_user_token_headers)

    assert response.status_code == 500
    assert "Orchestrator returned an error: Log retrieval failed" in response.text
    mock_send.assert_called_once_with({"action": "logs"})
    mock_await.assert_called_once_with(mock_command_id, timeout=10)


@patch("interface.api.v1.endpoints.system.send_command")
def test_get_system_logs_send_error(
    mock_send, client: TestClient, regular_user_token_headers: dict
):
    """Test scenario where sending the logs command via IPC fails."""
    mock_send.side_effect = OSError("IPC unavailable")

    response = client.get("/api/v1/system/logs", headers=regular_user_token_headers)

    assert response.status_code == 503
    assert "Failed to send command to orchestrator" in response.text
    mock_send.assert_called_once_with({"action": "logs"})


def test_get_system_logs_unauthenticated(client: TestClient):
    """Test accessing system logs endpoint without authentication."""
    response = client.get("/api/v1/system/logs")
    assert response.status_code == 401
    assert "Not authenticated" in response.text


# --- System Endpoints --- END ---

# --- Agent Dispatch Endpoint Tests ---


@pytest.mark.asyncio
async def test_dispatch_message_success(
    client: TestClient, regular_user_token_headers: dict, mocker
):
    """Test successfully dispatching a message to an agent."""
    agent_name = "architect"
    message = "Review the latest design doc."
    request_payload = {
        "message": message,
        "context": {"user_session": "xyz"},
        "tags": ["t1"],
        "task_owner": "tester",
        "payload": {"k": "v"},
    }

    mock_agent_response = "Acknowledged. Reviewing design doc now."
    mock_orchestrator_response_payload = {
        "status": "success",
        "agent_name": agent_name,
        "response": mock_agent_response,
        "request_id": "mock-req-id",
    }

    # Mock the _call_orchestrator helper used by the endpoint
    mock_call = mocker.patch(
        "interface.api.v1.endpoints.agents._call_orchestrator",
        return_value=mock_orchestrator_response_payload,
    )

    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/dispatch",
        headers=regular_user_token_headers,
        json=request_payload,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["agent_name"] == agent_name
    assert response_data["response"] == mock_agent_response
    assert response_data["request_id"] == "mock-req-id"

    # Verify the helper was called correctly
    mock_call.assert_called_once()
    call_args, _ = mock_call.call_args
    assert call_args[0]["action"] == "dispatch_agent_message"
    payload_sent = call_args[0]["payload"]
    assert payload_sent["agent_name"] == agent_name
    assert payload_sent["message"] == message
    assert payload_sent["context"] == request_payload["context"]
    assert payload_sent["originator"]["type"] == "user"
    assert payload_sent["tags"] == ["t1"]
    assert payload_sent["task_owner"] == "tester"
    assert payload_sent["payload"] == {"k": "v"}


@pytest.mark.asyncio
async def test_dispatch_message_agent_not_found(
    client: TestClient, regular_user_token_headers: dict, mocker
):
    """Test dispatching a message to an agent that doesn't exist."""
    agent_name = "ghost_agent"
    request_payload = {
        "message": "Are you there?",
        "tags": ["t2"],
        "task_owner": "tester",
    }

    mock_orchestrator_response_payload = {
        "status": "not_found",
        "detail": f"Agent {agent_name} not found.",
        "response": None,
    }

    mock_call = mocker.patch(
        "interface.api.v1.endpoints.agents._call_orchestrator",
        return_value=mock_orchestrator_response_payload,
    )

    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/dispatch",
        headers=regular_user_token_headers,
        json=request_payload,
    )

    assert response.status_code == 404  # Not Found
    assert f"Agent '{agent_name}' not found" in response.json()["detail"]
    mock_call.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_message_orchestrator_error(
    client: TestClient, regular_user_token_headers: dict, mocker
):
    """Test handling an orchestrator error during dispatch."""
    agent_name = "error_prone_agent"
    request_payload = {"message": "This might fail", "task_owner": "tester"}

    # Mock the helper raising an exception
    mock_call = mocker.patch(
        "interface.api.v1.endpoints.agents._call_orchestrator",
        side_effect=HTTPException(
            status_code=502, detail="Orchestrator error: Dispatch failed"
        ),
    )

    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/dispatch",
        headers=regular_user_token_headers,
        json=request_payload,
    )

    assert response.status_code == 502  # Bad Gateway
    assert "Orchestrator error: Dispatch failed" in response.json()["detail"]
    mock_call.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_message_unauthorized(client: TestClient):
    """Test dispatching a message without authentication."""
    agent_name = "any_agent"
    request_payload = {"message": "Test", "tags": ["t"], "task_owner": "tester"}
    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/dispatch", json=request_payload
    )
    assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_trigger_agent_assessment_success(
    client: TestClient, superuser_token_headers: dict, mocker
):
    """Test successfully triggering agent self-assessment as superuser."""
    agent_name = "architect"
    mock_orchestrator_response_payload = {
        "agent_name": agent_name,
        "status": "assessment_triggered",
        "message": "Assessment started",
        "request_id": "req-123",
    }
    mock_call = mocker.patch(
        "interface.api.v1.endpoints.agents._call_orchestrator",
        return_value=mock_orchestrator_response_payload,
    )

    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/assess",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == agent_name
    assert data["status"] == "assessment_triggered"
    assert data["message"] == "Assessment started"
    assert data["request_id"] == "req-123"
    mock_call.assert_called_once()
    call_args, _ = mock_call.call_args
    assert call_args[0]["action"] == "assess_agent"
    assert call_args[0]["payload"] == {"agent_name": agent_name}


@pytest.mark.asyncio
async def test_trigger_agent_assessment_agent_not_found(
    client: TestClient, superuser_token_headers: dict, mocker
):
    """Test triggering assessment for a non-existent agent returns 404."""
    agent_name = "ghost_agent"
    mock_orchestrator_response_payload = {
        "agent_name": agent_name,
        "status": "error",
        "message": "Agent not found",
        "request_id": "req-404",
    }
    mock_call = mocker.patch(
        "interface.api.v1.endpoints.agents._call_orchestrator",
        return_value=mock_orchestrator_response_payload,
    )

    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/assess",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert f"Agent '{agent_name}' not found" in response.json()["detail"]
    mock_call.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_agent_assessment_orchestrator_error(
    client: TestClient, superuser_token_headers: dict, mocker
):
    """Test orchestrator error during assessment trigger returns 502."""
    agent_name = "error_agent"
    mock_orchestrator_response_payload = {
        "agent_name": agent_name,
        "status": "error",
        "message": "Internal orchestrator error",
        "request_id": "req-err",
    }
    mock_call = mocker.patch(
        "interface.api.v1.endpoints.agents._call_orchestrator",
        return_value=mock_orchestrator_response_payload,
    )

    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/assess",
        headers=superuser_token_headers,
    )
    assert response.status_code == 502
    assert "Orchestrator failed to trigger assessment" in response.json()["detail"]
    mock_call.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_agent_assessment_forbidden(
    client: TestClient, regular_user_token_headers: dict
):
    """Test that a regular user cannot trigger agent assessment (403/400)."""
    agent_name = "architect"
    response = client.post(
        f"{settings.API_V1_STR}/agents/{agent_name}/assess",
        headers=regular_user_token_headers,
    )
    assert response.status_code in (400, 403)
    assert (
        "enough privileges" in response.text or "Not enough privileges" in response.text
    )
