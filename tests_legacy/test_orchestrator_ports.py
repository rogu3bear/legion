"""
Tests for orchestrator port loading and fallback logic.
"""

import os
from unittest.mock import patch

import pytest

from legion import ports as legion_ports  # To access the module-level RUNTIME_PORTS
from legion.orchestrator import Orchestrator

ENV_PORTS_CONTENT_VALID = """
PORT_ALLOCATOR_REDIS=1234
PORT_ALLOCATOR_POSTGRES=5678
# Comment line
INVALID_LINE
PORT_ALLOCATOR_GRAFANA=INVALID_PORT_VALUE
PORT_ALLOCATOR_WEB=8001
PORT_ALLOCATOR_CHROMA=27777 # Test override for chroma
"""

ENV_PORTS_CONTENT_EMPTY = """
# No valid ports defined
"""


# Fixture to ensure legion_ports.RUNTIME_PORTS is reset between tests
@pytest.fixture(autouse=True)
def reset_runtime_ports():
    original_runtime_ports = legion_ports.RUNTIME_PORTS.copy()
    original_default_ports = legion_ports.DEFAULT_PORTS.copy()
    yield
    legion_ports.RUNTIME_PORTS = original_runtime_ports
    legion_ports.DEFAULT_PORTS = original_default_ports
    legion_ports.load_runtime_ports()  # Reload original state or defaults


def test_port_loading_with_valid_env_file(tmp_path):
    """Test that .env.ports overrides defaults and handles some invalid lines."""
    env_file = tmp_path / ".env.ports"
    env_file.write_text(ENV_PORTS_CONTENT_VALID)

    # Patch out PortAllocator instantiation within Orchestrator if it's complex
    # For this test, we only care about load_runtime_ports and get_port
    with patch.object(Orchestrator, "_acquire_lock"), patch.object(
        Orchestrator, "init_zmq_pub_server"
    ), patch.object(Orchestrator, "init_zmq_rep_server"):
        # Ensure load_runtime_ports uses our temp file
        legion_ports.load_runtime_ports(env_file_path=str(env_file))

        assert legion_ports.get_port("redis") == 1234
        assert legion_ports.get_port("postgres") == 5678
        assert legion_ports.get_port("web") == 8001  # Overrides default 8000
        # Grafana had an invalid port value, should use default
        assert legion_ports.get_port("grafana") == legion_ports.DEFAULT_PORTS["grafana"]
        # Chroma is in .env.ports, should use the override
        assert legion_ports.get_port("chroma") == 27777
        # Prometheus was not in .env.ports, should use default
        assert (
            legion_ports.get_port("prometheus")
            == legion_ports.DEFAULT_PORTS["prometheus"]
        )
        # Orchestrator default
        assert (
            legion_ports.get_port("orchestrator")
            == legion_ports.DEFAULT_PORTS["orchestrator"]
        )


def test_port_loading_with_empty_env_file(tmp_path):
    """Test that defaults are used if .env.ports is empty or has no valid entries."""
    env_file = tmp_path / ".env.ports"
    env_file.write_text(ENV_PORTS_CONTENT_EMPTY)

    with patch.object(Orchestrator, "_acquire_lock"), patch.object(
        Orchestrator, "init_zmq_pub_server"
    ), patch.object(Orchestrator, "init_zmq_rep_server"):
        legion_ports.load_runtime_ports(env_file_path=str(env_file))

        assert legion_ports.get_port("redis") == legion_ports.DEFAULT_PORTS["redis"]
        assert (
            legion_ports.get_port("postgres") == legion_ports.DEFAULT_PORTS["postgres"]
        )
        assert (
            legion_ports.get_port("prometheus")
            == legion_ports.DEFAULT_PORTS["prometheus"]
        )
        assert legion_ports.get_port("grafana") == legion_ports.DEFAULT_PORTS["grafana"]
        assert legion_ports.get_port("web") == legion_ports.DEFAULT_PORTS["web"]
        assert (
            legion_ports.get_port("chroma") == legion_ports.DEFAULT_PORTS["chroma"]
        )  # Should use default


def test_port_loading_no_env_file():
    """Test that defaults are used if .env.ports does not exist."""
    # Ensure no .env.ports file exists by using a non-existent path for loading
    with patch.object(Orchestrator, "_acquire_lock"), patch.object(
        Orchestrator, "init_zmq_pub_server"
    ), patch.object(Orchestrator, "init_zmq_rep_server"):
        legion_ports.load_runtime_ports(env_file_path="non_existent_env_file.ports")

        assert legion_ports.get_port("redis") == legion_ports.DEFAULT_PORTS["redis"]
        assert (
            legion_ports.get_port("postgres") == legion_ports.DEFAULT_PORTS["postgres"]
        )
        assert legion_ports.get_port("web") == legion_ports.DEFAULT_PORTS["web"]
        assert (
            legion_ports.get_port("chroma") == legion_ports.DEFAULT_PORTS["chroma"]
        )  # Should use default


@patch.dict(os.environ, {"LEGION_DEBUG_PORTS": "true"})
@patch("legion.orchestrator.logger")  # Mock the orchestrator's logger
def test_orchestrator_startup_logs_banner(mock_logger, tmp_path):
    """Test that orchestrator logs the port banner when LEGION_DEBUG_PORTS is true."""
    env_file = tmp_path / ".env.ports"
    env_file.write_text(
        "PORT_ALLOCATOR_REDIS=1111\\nPORT_ALLOCATOR_WEB=2222\\nPORT_ALLOCATOR_CHROMA=3333"
    )

    with patch.object(Orchestrator, "_acquire_lock"), patch.object(
        Orchestrator, "init_zmq_pub_server"
    ), patch.object(Orchestrator, "init_zmq_rep_server"):
        # Critical: Ensure legion.ports reloads with the temp file for THIS test
        legion_ports.load_runtime_ports(env_file_path=str(env_file))
        Orchestrator()  # Instantiation calls _log_runtime_ports

    # Check if logger.info was called and if the banner is in the log messages
    banner_found = False
    expected_substrings = [
        "[orchestrator] dynamic ports ->",
        "redis:1111",
        "web:2222",
        "chroma:3333",
    ]
    for call_args in mock_logger.info.call_args_list:
        log_message = call_args[0][0]
        if all(sub in log_message for sub in expected_substrings):
            banner_found = True
            break
    assert (
        banner_found
    ), f"Port banner not found or incorrect in logs. Logs: {mock_logger.info.call_args_list}"


@patch.dict(os.environ, {"LEGION_DEBUG_PORTS": "false"})
@patch("legion.orchestrator.logger")
def test_orchestrator_startup_no_banner_if_debug_false(mock_logger, tmp_path):
    """Test that orchestrator does NOT log the port banner when LEGION_DEBUG_PORTS is false."""
    env_file = tmp_path / ".env.ports"
    env_file.write_text("PORT_ALLOCATOR_REDIS=1111")

    with patch.object(Orchestrator, "_acquire_lock"), patch.object(
        Orchestrator, "init_zmq_pub_server"
    ), patch.object(Orchestrator, "init_zmq_rep_server"):
        legion_ports.load_runtime_ports(env_file_path=str(env_file))
        Orchestrator()

    for call_args in mock_logger.info.call_args_list:
        log_message = call_args[0][0]
        assert (
            "[orchestrator] dynamic ports ->" not in log_message
        ), "Port banner logged when LEGION_DEBUG_PORTS was false"
