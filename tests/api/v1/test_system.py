from fastapi.testclient import TestClient

import pytest
from interface.core.config import settings


@pytest.mark.asyncio
async def test_get_system_logs(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    mock_response_payload = {
        "status": "success",
        "logs": [
            {
                "timestamp": "2023-10-01T10:00:00Z",
                "level": "INFO",
                "message": "Orchestrator started.",
            },
            {
                "timestamp": "2023-10-01T10:01:00Z",
                "level": "INFO",
                "message": "Agent initialized: architect_agent",
            },
        ],
    }
    # Mock the new send_request function
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request",
        return_value={"response": mock_response_payload},
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/logs",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.json() == mock_response_payload
    # Verify send_request was called with the correct action
    mock_send.assert_called_once_with(
        mocker.ANY
    )  # Use ANY or check dict containing 'action':'logs'
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "logs"


@pytest.mark.asyncio
async def test_get_system_status(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    mock_response_payload = {
        "status": "success",
        "orchestrator_status": "running",
        "pid": 12345,
        "active_agents": ["architect", "researcher"],
    }
    # Mock the new send_request function
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request",
        return_value={"response": mock_response_payload},
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/status",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.json() == mock_response_payload
    # Verify send_request was called with the correct action
    mock_send.assert_called_once_with(mocker.ANY)
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "status"


@pytest.mark.asyncio
async def test_get_system_metrics(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    mock_response_payload = {
        "status": "success",
        "metrics": {
            "cpu_usage": 45.5,
            "memory_usage_mb": 1024,
            "active_connections": 50,
        },
    }
    # Mock the new send_request function
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request",
        return_value={"response": mock_response_payload},
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/metrics",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.json() == mock_response_payload
    # Verify send_request was called with the correct action
    mock_send.assert_called_once_with(mocker.ANY)
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "metrics"


# Add tests for error cases (timeout, orchestrator error)
@pytest.mark.asyncio
async def test_get_system_status_timeout(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    # Mock send_request to return None (simulating timeout)
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request", return_value=None
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/status",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 504  # Gateway Timeout
    assert "No response received" in response.json()["detail"]
    mock_send.assert_called_once()
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "status"


@pytest.mark.asyncio
async def test_get_system_status_error(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    mock_error_response = {
        "response": {"status": "error", "detail": "Orchestrator component failed"}
    }
    # Mock send_request to return an error response from orchestrator
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request",
        return_value=mock_error_response,
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/status",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 502  # Bad Gateway
    assert (
        "Orchestrator error: Orchestrator component failed" in response.json()["detail"]
    )
    mock_send.assert_called_once()
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "status"


# --- Tests for /system/memory/stats ---


@pytest.mark.asyncio
async def test_get_memory_stats_success(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    """Test successful retrieval of memory stats."""
    mock_response_payload = {
        "status": "success",
        "memory_stats": {
            "vector_db_size_gb": 1.5,
            "sql_db_size_mb": 250,
            "total_documents": 10000,
            "total_tasks_logged": 500,
        },
    }
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request",
        return_value={"response": mock_response_payload},
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/memory/stats",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.json() == mock_response_payload
    mock_send.assert_called_once()
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "memory_stats"


@pytest.mark.asyncio
async def test_get_memory_stats_timeout(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    """Test timeout when getting memory stats."""
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request", return_value=None
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/memory/stats",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 504  # Gateway Timeout
    assert "No response received" in response.json()["detail"]
    mock_send.assert_called_once()
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "memory_stats"


@pytest.mark.asyncio
async def test_get_memory_stats_orchestrator_error(
    client: TestClient, normal_user_token_headers: dict, mocker
):
    """Test orchestrator error when getting memory stats."""
    mock_error_response = {
        "response": {"status": "error", "detail": "Memory subsystem unavailable"}
    }
    mock_send = mocker.patch(
        "interface.api.v1.endpoints.system.send_request",
        return_value=mock_error_response,
    )

    response = client.get(
        f"{settings.API_V1_STR}/system/memory/stats",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 502  # Bad Gateway
    assert (
        "Orchestrator error: Memory subsystem unavailable" in response.json()["detail"]
    )
    mock_send.assert_called_once()
    call_args, _ = mock_send.call_args
    assert call_args[0]["action"] == "memory_stats"


# --- End Tests for /system/memory/stats ---
