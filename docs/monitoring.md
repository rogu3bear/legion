# Monitoring & Metrics

Legion now exposes Prometheus metrics for operational monitoring.

## Starting the metrics server

Import and start the HTTP endpoint before running the orchestrator:

```python
from metrics.exporter import start_metrics_server

# Start on port 8000 (default)
start_metrics_server(port=8000)

# Then start the orchestrator normally
from legion.orchestrator import Orchestrator
Orchestrator(...).run()
```

## Available Metrics

- `legion_dispatch_total{agent_key="..."}`: Counter of dispatch calls per agent.
- `legion_dispatch_latency_seconds_bucket{agent_key="..."}`: Histogram buckets for dispatch latency.
- `legion_dispatch_latency_seconds_sum{agent_key="..."}`: Sum of all latencies.
- `legion_dispatch_latency_seconds_count{agent_key="..."}`: Total observations count.

## Grafana Dashboard Snippet

Below is a minimal Grafana dashboard JSON snippet to visualize 95th percentile latency:

```json
{
  "panels": [
    {
      "type": "graph",
      "title": "Dispatch Latency (95th percentile)",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(legion_dispatch_latency_seconds_bucket[5m])) by (agent_key, le))",
          "legendFormat": "{{agent_key}}",
          "refId": "A"
        }
      ],
      "yaxes": [
        {"format": "s", "label": "Latency (s)"},
        {"format": "short"}
      ]
    }
  ]
}
```

## Port Management for Legion Services

Legion's services, including Prometheus, web interfaces, and internal components like Chroma, rely on a unified port management system defined in `legion/ports.py`. This system uses a dictionary of `DEFAULT_PORTS` and allows overrides via a `.env.ports` file located in the project root.

**Key Files & Concepts:**

*   **`legion/ports.py`**: Contains the `DEFAULT_PORTS` dictionary with default port assignments for various services. It also includes the `load_runtime_ports()` function that merges these defaults with overrides from `.env.ports`, and the `get_port(service_key)` utility to retrieve the currently active port for a service.
*   **`.env.ports`**: An optional file in the project root. If it exists, it can override default ports. Variables should be in the format `PORT_ALLOCATOR_SERVICEKEY=port_number` (e.g., `PORT_ALLOCATOR_PROMETHEUS=9091`).
*   **`get_port(service_key)`**: The canonical way to get a service's port at runtime (e.g., `from legion.ports import get_port; port = get_port('prometheus')`).
*   **`ports.yaml`**: This file contains a static map of ports, often with a group/key structure. While not directly used by the core runtime for port resolution (which uses `legion/ports.py`), it can serve as a reference or be used by utility scripts that generate specific environment configurations (like an older version of `scripts/generate_docker_env.py`). The primary runtime truth comes from `legion/ports.py` and `.env.ports`.

To find the currently configured port for a service like Prometheus, you should check `legion/ports.py` for its default and then see if `.env.ports` overrides it. The `legion cli ports` command can also show currently resolved ports at runtime if the orchestrator components are accessible.

For more detailed information on the port strategy, including a list of all default service keys, see `docs/port_strategy.md`.

## Launching Services

When launching services (e.g., via `docker-compose` or other means), ensure they are configured to use the ports defined in `ports.yaml`.

For example, if Prometheus is defined in `ports.yaml` as:
```yaml
services:
  prometheus: 9090
```
Your `docker-compose.yml` or service startup script should use port `9090` for Prometheus.

Then verify readiness (e.g., Prometheus):

```bash
# Get the current Prometheus port (e.g., from legion.ports.get_port('prometheus') or .env.ports)
# For example, if it resolves to 9090:
curl -f "http://localhost:9090/-/ready"
```

### Current Port Map
| Service        | Host Port |
| -------------- | --------- |
