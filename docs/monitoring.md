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



## Port Management with `ports.yaml`

Legion utilizes `UnifiedPortManager` for port assignments, configured via `ports.yaml` at the project root. This file defines static ports or dynamic port ranges for all services, including Prometheus.

Refer to `ports.yaml` in the project root to find the currently configured port for Prometheus (typically under the `services.prometheus` key).

For detailed information on port configuration, see `docs/orchestrator.md`.

## Launching Services

When launching services (e.g., via `docker-compose` or other means), ensure they are configured to use the ports defined in `ports.yaml`.

For example, if Prometheus is defined in `ports.yaml` as:
```yaml
services:
  prometheus: 9090
```
Your `docker-compose.yml` or service startup script should use port `9090` for Prometheus.

Then verify readiness (e.g., Prometheus, assuming it's on port 9090 as per `ports.yaml`):

```bash
# First, check ports.yaml to find the Prometheus port (e.g., 9090)
# Then use that port in your command:
curl -f "http://localhost:9090/-/ready" # Replace 9090 with the actual port from ports.yaml
```

### Current Port Map
| Service        | Host Port |
| -------------- | --------- |
