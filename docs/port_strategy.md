# Legion Port Management Strategy

> **TODO**: Update this document to reflect the current fixed port map `7801-7810`.

This document outlines how network ports are managed across the Legion application, covering development, testing, and production environments.

## Core Mechanism

The primary mechanism for port management resides in `legion/ports.py`. It defines:

1.  **`DEFAULT_PORTS`**: A Python dictionary mapping service keys (strings) to default integer port numbers. This is the baseline configuration.
2.  **`.env.ports` file**: An optional environment file that can be placed in the project root. If present, it can override the `DEFAULT_PORTS`. Variables in this file must follow the pattern `PORT_ALLOCATOR_<SERVICE_KEY_UPPERCASE>=<port_number>` (e.g., `PORT_ALLOCATOR_WEB=8001`).
3.  **`load_runtime_ports()` function**: Called on module load (and can be called explicitly), this function populates an internal `RUNTIME_PORTS` dictionary by first loading `DEFAULT_PORTS` and then applying any overrides from `.env.ports`.
4.  **`get_port(service_key: str)` function**: This is the **canonical way** for any part of the Legion application to retrieve the currently configured port for a given service. It queries the `RUNTIME_PORTS`.

## Service Keys in `DEFAULT_PORTS`

As of the last update, the following service keys are defined with their default ports in `legion/ports.py`:

*   `web`: 8000 (Standard for FastAPI/Uvicorn)
*   `orchestrator`: 5555 (Default ZMQ/IPC for orchestrator)
*   `redis`: 6379
*   `postgres`: 5432
*   `prometheus`: 9090
*   `grafana`: 7806
*   `dev_frontend`: 8000 (Matches Docker Compose `web` service host port variable)
*   `chroma`: 27020 (Default port for ChromaDB)

## Environment-Specific Configurations

*   **Local Development**: Developers can use a local `.env.ports` to customize ports if defaults conflict or specific ports are needed. `docker-compose.yml` also uses variables (e.g., `${PORT_ALLOCATOR_DEV_FRONTEND}`) that can be sourced from this file.
*   **Testing**: Tests can rely on default ports or use a temporary `.env.ports` file for specific test scenarios (see `tests/test_orchestrator_ports.py`).
*   **Production**: Production deployments should use a `.env.ports` file managed securely (e.g., via CI/CD secrets or configuration management tools) to define the correct ports for that environment.

## Key Scripts

*   **`scripts/gen_ports_env.sh`**: Generates a `.env.ports` file. This is useful for CI or setting up environments quickly. It iterates through a predefined list of services (which should be kept in sync with `DEFAULT_PORTS` keys needing exposure via this method) and assigns them ports (currently from a simple local allocator for the script's purpose, but the generated file is what matters for `load_runtime_ports`).
*   **`scripts/generate_docker_env.py`**: Generates a `.env.docker-compose` file by querying `legion.ports.get_port()` for services defined in its internal `port_mappings`. This file is intended for Docker Compose setups that might need a different set of environment variable names than `PORT_ALLOCATOR_*`.

## ChromaDB Port Configuration

*   The default port for ChromaDB is managed via the `chroma` key in `DEFAULT_PORTS` (defaulting to `27020`).
*   The middleware service (`middleware/src/config.py`) retrieves the Chroma API URL by calling `legion.ports.get_chroma_url()`. This helper function internally uses `legion.ports.get_port('chroma')` to construct the full URL (e.g., `http://localhost:27020`).
*   This allows the Chroma URL to be consistently configured via the unified port management system and overridden by `PORT_ALLOCATOR_CHROMA` in `.env.ports` if needed.

## Viewing Resolved Ports

The Legion CLI provides a command to view the currently resolved ports:

```bash
legion ports
```

This command internally calls `legion.ports.load_runtime_ports()` and then accesses `legion.ports.RUNTIME_PORTS` to display the active port for each configured service, reflecting `DEFAULT_PORTS` and any `.env.ports` (or environment-specific `.env.*`) overrides.
