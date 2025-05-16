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

## Development Overrides with Docker Compose

For local development, you can customize service configurations, such as host port bindings, using a `docker-compose.override.dev.yml` file. This file is not typically committed to the repository and allows for local adjustments without altering the main `docker-compose.yml`.

To override a host port, ensure your main `docker-compose.yml` uses environment variables for port definitions (e.g., `${PORT_ALLOCATOR_SERVICES_WEB_UI}`). Then, you can specify these variables in your `.env.ports` file. Docker Compose will automatically pick up values from `.env` (and by extension, `.env.ports` if your `ports.py` logic loads it into the environment or if you source it).

**Example: Overriding the Web UI host port**

1.  **Ensure `docker-compose.yml` uses a variable for the host port:**

    ```yaml
    # In docker-compose.yml
    services:
      web_ui:
        ports:
          - "${PORT_ALLOCATOR_SERVICES_WEB_UI}:27000" # Host port is variable, container port is fixed
    ```

2.  **Define the desired host port in `.env.ports`:**

    ```dotenv
    # In .env.ports
    PORT_ALLOCATOR_SERVICES_WEB_UI=27001
    ```

3.  **(Optional) Create or modify `docker-compose.override.dev.yml` for other dev settings (e.g., volume mounts for hot-reloading):**

    ```yaml
    # In docker-compose.override.dev.yml
    version: '3.8'
    services:
      web_ui:
        volumes:
          - ./interface:/app/interface # Example: Mount local code for hot-reloading
        # No need to redefine ports here if already handled by .env.ports and main compose file.
    ```

When you run `docker compose -f docker-compose.yml -f docker-compose.override.dev.yml up` (or just `docker compose up` if Docker Compose automatically picks up the override), the `web_ui` service will be accessible on host port `27001` (or whatever you set in `.env.ports`).

```bash
# Example: run UI on custom host port
echo "PORT_ALLOCATOR_WEB=31000" >> .env.ports
docker compose up web_ui # or docker compose up -d web_ui
```

This approach keeps your base `docker-compose.yml` clean and allows each developer to customize ports and other settings locally via `.env.ports` and an override file.
