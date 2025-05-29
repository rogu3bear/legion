#!/usr/bin/env python3
"""
Prometheus metrics exporter for Legion.
"""

from prometheus_client import Counter, Histogram, start_http_server

from legion.ports import get_port

# Metrics definitions
# Count total dispatch calls per agent_key
dispatch_counter = Counter(
    "legion_dispatch_total", "Total number of dispatch calls", ["agent_key"]
)
# Histogram of dispatch latency per agent_key
dispatch_latency = Histogram(
    "legion_dispatch_latency_seconds", "Dispatch latency in seconds", ["agent_key"]
)


def start_metrics_server(port: int | None = None) -> None:
    """
    Start Prometheus metrics HTTP server on the specified port.
    """
    if port is None:
        port = get_port("metrics") or 7606
    start_http_server(port)
