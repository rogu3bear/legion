import multiprocessing
import socket
import time
from unittest.mock import patch

from prometheus_client import generate_latest

from legion.ports import get_port
from metrics.exporter import dispatch_counter, dispatch_latency, start_metrics_server


def is_port_in_use(port: int) -> bool:
    """Check if a port is currently in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(("localhost", port))
        return result == 0


def test_metrics_definitions():
    # Ensure metrics are registered
    output = generate_latest()
    text = output.decode("utf-8")
    assert "legion_dispatch_total" in text
    assert "legion_dispatch_latency_seconds_bucket" in text


def test_metrics_server_start(monkeypatch):
    calls = {}

    def fake_start(port):
        calls["port"] = port

    monkeypatch.setattr("metrics.exporter.start_http_server", fake_start)
    metrics_port = get_port("test_metrics_server")
    if metrics_port is None:  # Fallback if not configured
        metrics_port = 9100  # Default for tests
    start_metrics_server(port=metrics_port)
    assert calls.get("port") == metrics_port


def test_record_metrics():
    # Record one dispatch
    counter_before = dispatch_counter.labels(agent_key="foo")._value.get()
    histogram_before = dispatch_latency.labels(agent_key="foo")._sum.get()

    dispatch_counter.labels(agent_key="foo").inc()
    dispatch_latency.labels(agent_key="foo").observe(0.123)

    counter_after = dispatch_counter.labels(agent_key="foo")._value.get()
    histogram_after = dispatch_latency.labels(agent_key="foo")._sum.get()

    assert counter_after == counter_before + 1
    assert histogram_after >= histogram_before + 0.123


def test_start_metrics_server_custom_port(prometheus_multiproc_fixture):
    # Ensure the server can start on a custom port if available
    custom_port = get_port("test_metrics_server")  # Use a specific key for test metrics
    assert custom_port is not None, "Port for test_metrics_server not configured"
    # For testing, we might need to ensure this port is not the default prometheus port
    # if they are intended to be different.
    # This test assumes get_port will provide a usable port, potentially 9100 via config.

    process = multiprocessing.Process(target=start_metrics_server, args=(custom_port,))
    process.start()
    time.sleep(0.5)  # Give time for the server to start

    assert is_port_in_use(
        custom_port
    ), f"Port {custom_port} should be in use by metrics server"


@patch("prometheus_client.start_http_server")
def test_start_metrics_server_default_port(mock_start_http_server):
    port_to_use = get_port("test_metrics_server")
    if port_to_use is None:  # Fallback if not in config
        port_to_use = 9100  # Default for tests

    start_metrics_server(port=port_to_use)
    mock_start_http_server.assert_called_once_with(port_to_use)
