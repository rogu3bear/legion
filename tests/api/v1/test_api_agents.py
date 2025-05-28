from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

# Assuming your FastAPI app instance is created in interface.main
# Adjust the import path if necessary
from interface.main import app
from interface.schemas.agent import (
    AgentActionResponse
    AgentConfigInfo
    AgentStatusInfo
)

# Use a synchronous test client for simplicity in these examples
client = TestClient(app)

# --- Mock Data ---
MOCK_AGENT_LIST = [
    {"name": "Doctor", "status": "running", "tasks": 1}
    {"name": "Researcher", "status": "idle", "tasks": 0}
]

MOCK_DOCTOR_STATUS = {
    "name": "Doctor"
    "status": "running"
    "tasks": 1
    "cpu_usage": 10.5
    "memory_usage": 256.0
    "last_heartbeat": "2023-10-27T10:00:00Z"
}

MOCK_DOCTOR_CONFIG = {
    "agent_name": "Doctor"
    "llm_model": "gpt-4"
    "temperature": 0.7
    "max_tokens": 1000
    "description": "Provides medical advice."
}

MOCK_NOT_FOUND_RESPONSE = {"error": "Agent not found"}
MOCK_COMM_FAILURE_RESPONSE = {"error": "Orchestrator communication failed"}

# --- Test Cases ---


@pytest.mark.parametrize(
    "mock_response, expected_status, expected_json"
    [
        (MOCK_AGENT_LIST, 200, MOCK_AGENT_LIST)
        (MOCK_COMM_FAILURE_RESPONSE, 503, MOCK_COMM_FAILURE_RESPONSE)
        ([], 200, []),  # Test empty list case
    ]
)
@patch("interface.orchestrator_comm.send_orchestrator_request")
def test_list_agents(mock_send_request, mock_response, expected_status, expected_json):
    """Tests GET /agents endpoint."""
    mock_send_request.return_value = mock_response

    response = client.get("/api/v1/agents")

    assert response.status_code == expected_status
    assert response.json() == expected_json
    mock_send_request.assert_called_once_with(action="list_agents", payload={})


@pytest.mark.parametrize(
    "agent_name, mock_response, expected_status, expected_json"
    [
        ("Doctor", MOCK_DOCTOR_STATUS, 200, MOCK_DOCTOR_STATUS)
        ("NonExistent", MOCK_NOT_FOUND_RESPONSE, 404, MOCK_NOT_FOUND_RESPONSE)
        ("Doctor", MOCK_COMM_FAILURE_RESPONSE, 503, MOCK_COMM_FAILURE_RESPONSE)
    ]
)
@patch("interface.orchestrator_comm.send_orchestrator_request")
def test_get_agent_status(
    mock_send_request, agent_name, mock_response, expected_status, expected_json
):
    """Tests GET /agents/{agent_name} endpoint."""
    mock_send_request.return_value = mock_response

    response = client.get(f"/api/v1/agents/{agent_name}")

    assert response.status_code == expected_status
    # Pydantic models automatically handle parsing here if response is valid
    # For error cases, we compare directly with the expected JSON
    if expected_status == 200:
        # Assuming AgentStatusInfo is the response model
        assert AgentStatusInfo(**response.json()) == AgentStatusInfo(**expected_json)
    else:
        assert response.json() == expected_json

    mock_send_request.assert_called_once_with(
        action="get_agent_status", payload={"agent_name": agent_name}
    )


@pytest.mark.parametrize(
    "agent_name, mock_response, expected_status, expected_json"
    [
        ("Doctor", MOCK_DOCTOR_CONFIG, 200, MOCK_DOCTOR_CONFIG)
        ("NonExistent", MOCK_NOT_FOUND_RESPONSE, 404, MOCK_NOT_FOUND_RESPONSE)
        ("Doctor", MOCK_COMM_FAILURE_RESPONSE, 503, MOCK_COMM_FAILURE_RESPONSE)
    ]
)
@patch("interface.orchestrator_comm.send_orchestrator_request")
def test_get_agent_config(
    mock_send_request, agent_name, mock_response, expected_status, expected_json
):
    """Tests GET /agents/{agent_name}/config endpoint."""
    mock_send_request.return_value = mock_response

    response = client.get(f"/api/v1/agents/{agent_name}/config")

    assert response.status_code == expected_status
    if expected_status == 200:
        # Assuming AgentConfigInfo is the response model
        assert AgentConfigInfo(**response.json()) == AgentConfigInfo(**expected_json)
    else:
        assert response.json() == expected_json

    mock_send_request.assert_called_once_with(
        action="get_agent_config", payload={"agent_name": agent_name}
    )


# --- Tests for Lifecycle Control Endpoints ---


def test_start_agent_success(client: TestClient, superuser_token_headers: dict):
    """Test starting an agent successfully (mocked orchestrator)."""
    agent_name = "test_agent"
    # Mock the crud function to return a successful response
    with patch(
        "interface.crud.crud_agent.control_agent_lifecycle"
        return_value=AgentActionResponse(
            agent_name=agent_name
            action="start_agent"
            status="success"
            detail="Agent started."
        )
    ):
        response = client.post(
            f"/api/v1/agents/{agent_name}/start", headers=superuser_token_headers
        )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["agent_name"] == agent_name
    assert data["action"] == "start_agent"
    assert data["status"] == "success"
    assert data["detail"] == "Agent started."


def test_start_agent_not_found(client: TestClient, superuser_token_headers: dict):
    """Test starting an agent that doesn't exist."""
    agent_name = "non_existent_agent"
    with patch(
        "interface.crud.crud_agent.control_agent_lifecycle"
        return_value=AgentActionResponse(
            agent_name=agent_name
            action="start_agent"
            status="error"
            detail=f"Agent '{agent_name}' not found."
        )
    ):
        response = client.post(
            f"/api/v1/agents/{agent_name}/start", headers=superuser_token_headers
        )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_start_agent_orchestrator_error(
    client: TestClient, superuser_token_headers: dict
):
    """Test orchestrator error when starting agent."""
    agent_name = "error_agent"
    with patch(
        "interface.crud.crud_agent.control_agent_lifecycle"
        return_value=AgentActionResponse(
            agent_name=agent_name
            action="start_agent"
            status="error"
            detail="Orchestrator internal error."
        )
    ):
        response = client.post(
            f"/api/v1/agents/{agent_name}/start", headers=superuser_token_headers
        )
    assert response.status_code == status.HTTP_502_BAD_GATEWAY


def test_start_agent_no_permission(client: TestClient, normal_user_token_headers: dict):
    """Test starting agent without superuser permissions."""
    response = client.post(
        "/api/v1/agents/test_agent/start", headers=normal_user_token_headers
    )
    assert (
        response.status_code == status.HTTP_403_FORBIDDEN
    )  # Assuming 403 Forbidden for permission errors


def test_stop_agent_success(client: TestClient, superuser_token_headers: dict):
    """Test stopping an agent successfully."""
    agent_name = "test_agent"
    with patch(
        "interface.crud.crud_agent.control_agent_lifecycle"
        return_value=AgentActionResponse(
            agent_name=agent_name
            action="stop_agent"
            status="success"
            detail="Agent stopped."
        )
    ):
        response = client.post(
            f"/api/v1/agents/{agent_name}/stop", headers=superuser_token_headers
        )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"


def test_restart_agent_success(client: TestClient, superuser_token_headers: dict):
    """Test restarting an agent successfully."""
    agent_name = "test_agent"
    with patch(
        "interface.crud.crud_agent.control_agent_lifecycle"
        return_value=AgentActionResponse(
            agent_name=agent_name
            action="restart_agent"
            status="success"
            detail="Agent restarted."
        )
    ):
        response = client.post(
            f"/api/v1/agents/{agent_name}/restart", headers=superuser_token_headers
        )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"


# --- Tests for Reload Config Endpoint ---


def test_reload_configs_success(client: TestClient, superuser_token_headers: dict):
    """Test reloading agent configs successfully (mocked orchestrator)."""
    # Mock the crud function to return a successful response
    with patch(
        "interface.crud.crud_agent.reload_agent_configurations"
        return_value=AgentActionResponse(
            agent_name="all"
            action="reload_configs"
            status="success"
            detail="Agent configurations reloaded successfully."
        )
    ) as mock_reload:
        response = client.post("/api/v1/agents/reload", headers=superuser_token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["agent_name"] == "all"
    assert data["action"] == "reload_configs"
    assert data["status"] == "success"
    assert data["detail"] == "Agent configurations reloaded successfully."
    mock_reload.assert_called_once()


def test_reload_configs_orchestrator_error(
    client: TestClient, superuser_token_headers: dict
):
    """Test orchestrator error during reload configs."""
    # Mock the crud function to return an error response
    with patch(
        "interface.crud.crud_agent.reload_agent_configurations"
        return_value=AgentActionResponse(
            agent_name="all"
            action="reload_configs"
            status="error"
            detail="Orchestrator communication failed."
        )
    ) as mock_reload:
        response = client.post("/api/v1/agents/reload", headers=superuser_token_headers)

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    data = response.json()
    assert "detail" in data
    assert "Orchestrator communication failed" in data["detail"]
    mock_reload.assert_called_once()


def test_reload_configs_no_permission(
    client: TestClient, normal_user_token_headers: dict
):
    """Test reloading configs without superuser permissions."""
    response = client.post("/api/v1/agents/reload", headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- Tests for Update Agent Config Endpoint ---


def test_update_agent_config_success(client: TestClient, superuser_token_headers: dict):
    """Test updating agent configuration successfully (mocked orchestrator)."""
    agent_name = "test_agent"
    config_data = {"model": "gpt-4", "temperature": 0.7, "max_tokens": 2000}
    with patch(
        "interface.crud.crud_agent.update_agent_config"
        return_value=AgentActionResponse(
            agent_name=agent_name
            action="update_config"
            status="success"
            detail="Configuration updated successfully."
        )
    ) as mock_update:
        response = client.put(
            f"/api/v1/agents/{agent_name}/config"
            json=config_data
            headers=superuser_token_headers
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["agent_name"] == agent_name
    assert data["action"] == "update_config"
    assert data["status"] == "success"
    assert data["detail"] == "Configuration updated successfully."
    mock_update.assert_called_once()


def test_update_agent_config_not_found(
    client: TestClient, superuser_token_headers: dict
):
    """Test updating configuration for a non-existent agent."""
    agent_name = "non_existent_agent"
    config_data = {"model": "gpt-4", "temperature": 0.7, "max_tokens": 2000}
    with patch(
        "interface.crud.crud_agent.update_agent_config"
        return_value=AgentActionResponse(
            agent_name=agent_name
            action="update_config"
            status="error"
            detail=f"Agent '{agent_name}' not found."
        )
    ) as mock_update:
        response = client.put(
            f"/api/v1/agents/{agent_name}/config"
            json=config_data
            headers=superuser_token_headers
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_update.assert_called_once()


def test_update_agent_config_no_permission(
    client: TestClient, normal_user_token_headers: dict
):
    """Test updating agent configuration without superuser permissions."""
    agent_name = "test_agent"
    config_data = {"model": "gpt-4", "temperature": 0.7, "max_tokens": 2000}
    response = client.put(
        f"/api/v1/agents/{agent_name}/config"
        json=config_data
        headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- Tests for Dispatch Endpoint ---


def test_dispatch_message_success(client: TestClient, normal_user_token_headers: dict):
    """Test dispatching a message to an agent successfully (mocked orchestrator)."""
    agent_name = "test_agent"
    dispatch_data = {"message": "Hello, agent!", "context": {"key": "value"}}
    mock_response = {
        "agent_name": agent_name
        "response": "Hello, user!"
        "request_id": "12345"
    }
    with patch(
        "interface.api.v1.endpoints.system._call_orchestrator"
        return_value=mock_response
    ) as mock_call:
        response = client.post(
            f"/api/v1/agents/{agent_name}/dispatch"
            json=dispatch_data
            headers=normal_user_token_headers
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["agent_name"] == agent_name
    assert data["response"] == "Hello, user!"
    assert "request_id" in data
    mock_call.assert_called_once()


def test_dispatch_message_not_found(
    client: TestClient, normal_user_token_headers: dict
):
    """Test dispatching a message to a non-existent agent."""
    agent_name = "non_existent_agent"
    dispatch_data = {"message": "Hello, agent!", "context": {"key": "value"}}
    mock_response = {
        "status": "not_found"
        "detail": f"Agent '{agent_name}' not found."
    }
    with patch(
        "interface.api.v1.endpoints.system._call_orchestrator"
        return_value=mock_response
    ) as mock_call:
        response = client.post(
            f"/api/v1/agents/{agent_name}/dispatch"
            json=dispatch_data
            headers=normal_user_token_headers
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_call.assert_called_once()


# --- Tests for Assess Endpoint ---


def test_assess_agent_success(client: TestClient, superuser_token_headers: dict):
    """Test triggering self-assessment for an agent successfully (mocked orchestrator)."""
    agent_name = "test_agent"
    mock_response = {
        "status": "assessment_triggered"
        "message": "Assessment started for test_agent."
        "agent_name": agent_name
        "request_id": "12345"
    }
    with patch(
        "interface.api.v1.endpoints.system._call_orchestrator"
        return_value=mock_response
    ) as mock_call:
        response = client.post(
            f"/api/v1/agents/{agent_name}/assess", headers=superuser_token_headers
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["agent_name"] == agent_name
    assert data["status"] == "assessment_triggered"
    assert "message" in data
    mock_call.assert_called_once()


def test_assess_agent_not_found(client: TestClient, superuser_token_headers: dict):
    """Test triggering self-assessment for a non-existent agent."""
    agent_name = "non_existent_agent"
    mock_response = {
        "status": "error"
        "message": f"Agent '{agent_name}' not found."
        "agent_name": agent_name
    }
    with patch(
        "interface.api.v1.endpoints.system._call_orchestrator"
        return_value=mock_response
    ) as mock_call:
        response = client.post(
            f"/api/v1/agents/{agent_name}/assess", headers=superuser_token_headers
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_call.assert_called_once()


def test_assess_agent_no_permission(
    client: TestClient, normal_user_token_headers: dict
):
    """Test triggering self-assessment without superuser permissions."""
    agent_name = "test_agent"
    response = client.post(
        f"/api/v1/agents/{agent_name}/assess", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
