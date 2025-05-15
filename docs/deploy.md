# Deployment Guide

## Port Management

Ports for various services used by Legion are managed dynamically through `legion/ports.py`.
Configuration is primarily sourced from an `.env.ports` file, which should be generated from `ports.yaml` (legacy) using the `scripts/gen_env_ports.py` script:

```bash
python scripts/gen_env_ports.py ports.yaml > .env.ports.example
cp .env.ports.example .env.ports
```

`.env.ports` contains entries like `PORT_ALLOCATOR_SERVICE_NAME=12345`.
`legion/ports.py` provides default fallbacks if a port is not defined in `.env.ports`.

## Agent Configuration Placeholders

Certain agent configuration YAML files (e.g., `legion/configs/developer.yaml`) may contain placeholders for values that need to be dynamically inserted at runtime.

### Prometheus Port Example

The `developer.yaml` (and potentially other agent configurations) uses a placeholder `{{LEGION_PROMETHEUS_PORT}}` for its Prometheus metrics endpoint port:

```yaml
metrics:
  enabled: true
  prometheus_port: "{{LEGION_PROMETHEUS_PORT}}"
  collect_interval_seconds: 60
```

When `legion/orchestrator.py` loads these agent configuration files, it will automatically replace the `{{LEGION_PROMETHEUS_PORT}}` string with the actual port number obtained by calling `get_port("prometheus")` from `legion/ports.py`.

This ensures that the agent uses the correct, centrally managed port for Prometheus, which might be overridden by `.env.ports` or use the default specified in `legion/ports.py`.
