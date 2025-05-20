import pytest
from legion.utils.port_conflict_checker import (
    check_ports_available,
    validate_port_range,
)


def test_validate_port_range():
    # Development range (27000-28000)
    assert validate_port_range(27000, "development")
    assert validate_port_range(27500, "development")
    assert validate_port_range(28000, "development")
    assert not validate_port_range(26999, "development")
    assert not validate_port_range(28001, "development")

    # Production range (31000-32000)
    assert validate_port_range(31000, "production")
    assert validate_port_range(31500, "production")
    assert validate_port_range(32000, "production")
    assert not validate_port_range(30999, "production")
    assert not validate_port_range(32001, "production")

    # Testing range (29000-30000)
    assert validate_port_range(29000, "testing")
    assert validate_port_range(29500, "testing")
    assert validate_port_range(30000, "testing")
    assert not validate_port_range(28999, "testing")
    assert not validate_port_range(30001, "testing")

    # Invalid environment
    with pytest.raises(ValueError):
        validate_port_range(27000, "invalid")


def test_check_ports_available_range_violation():
    # Test range violations
    with pytest.raises(RuntimeError, match="Port range violations detected"):
        check_ports_available(
            {
                "service1": 26999,  # Below dev range
                "service2": 28001,  # Above dev range
            }
        )

    with pytest.raises(RuntimeError, match="Port range violations detected"):
        check_ports_available(
            {
                "service1": 30999,  # Below prod range
                "service2": 32001,  # Above prod range
            },
            environment="production",
        )


def test_check_ports_available_conflicts(mocker):
    # Mock socket.socket to simulate port conflicts
    calls = []

    # Create a mock socket using the context manager approach
    mock_socket = mocker.MagicMock()
    mock_socket.__enter__.return_value = mock_socket

    def mock_bind(addr):
        port = addr[1]
        calls.append(port)
        raise OSError("Address already in use")

    # Assign the bind method to our mock socket
    mock_socket.bind = mock_bind

    # Replace the socket constructor
    mocker.patch("socket.socket", return_value=mock_socket)

    with pytest.raises(RuntimeError, match="Port conflicts detected"):
        check_ports_available({"service1": 27000, "service2": 27001})

    # Verify that all ports were attempted
    assert 27000 in calls
    assert 27001 in calls


def test_check_ports_available_success(mocker):
    # Mock socket.socket to simulate available ports
    calls = []

    # Create a mock socket using the context manager approach
    mock_socket = mocker.MagicMock()
    mock_socket.__enter__.return_value = mock_socket

    def mock_bind(addr):
        port = addr[1]
        calls.append(port)
        # No exception means ports are available
        pass

    # Assign the bind method to our mock socket
    mock_socket.bind = mock_bind

    # Replace the socket constructor
    mocker.patch("socket.socket", return_value=mock_socket)

    # Should not raise any exceptions
    check_ports_available({"service1": 27000, "service2": 27001})

    # Verify all ports were checked
    assert 27000 in calls
    assert 27001 in calls


def test_skip_lmstudio_port(mocker):
    # LMStudio port 1234 should be skipped and not checked for conflicts
    calls = []

    # Instead of mocking socket.socket.bind directly, mock socket's context manager
    mock_socket = mocker.MagicMock()
    mock_socket.__enter__.return_value = mock_socket

    def mock_bind(addr):
        port = addr[1]  # Extract port from ("0.0.0.0", port)
        calls.append(port)
        if port == 27000:
            raise OSError("Address already in use")

    # Assign the bind method to our mock socket
    mock_socket.bind = mock_bind

    # Replace the socket constructor
    mocker.patch("socket.socket", return_value=mock_socket)

    # Should raise for service1, but not for LMStudio
    with pytest.raises(RuntimeError, match="Port conflicts detected"):
        check_ports_available({"lmstudio": 1234, "service1": 27000})

    # Ensure bind was attempted only for 27000, not for 1234
    assert 1234 not in calls
    assert 27000 in calls
