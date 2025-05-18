import os

DEFAULT_PORTS = {
    "orchestrator": 5555,
    "web_ui": 8000,
    "chroma": 27020,
    "prometheus": 9090,
    "redis": 6379,
    "postgres": 5432,
    "grafana": int(os.getenv("GRAFANA_PORT", 7806)),
    "orchestrator_zmq_pub": 7808,
    "orchestrator_zmq_rep": 7809,
    "orchestrator_api": 7803,
}
