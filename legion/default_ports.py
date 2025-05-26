DEFAULT_PORTS = {
    "ui_backend": 7801,
    "ui_frontend": 7802,
    "orchestrator_rest": 7803,
    "interface_api": 7804,
    "middleware": 7805,
    "metrics": 7806,
    "researcher_api": 7807,
    "zmq_pub": 7808,
    "zmq_sub": 7809,
    "redis": 7810,
    "web": 27001,  # Web UI port - changed from 8000 to 27001 to avoid conflicts
    "chroma": 27020,  # ChromaDB port
    "prometheus": 27030,  # Prometheus metrics port
    "postgres": 27050,  # PostgreSQL port
    "grafana": 27060,  # Grafana port
    "orchestrator": 27000,  # Orchestrator port
}
