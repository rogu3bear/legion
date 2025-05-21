# Legion Codebase Snapshot (2025-05-21T01:57:47.712713)

## Overview
Legion orchestrates specialized agents via a layered architecture defined in `docs/architecture.md`. Core layers include configuration, core services, agents, memory, integration, and skills.

## Module Breakdown
- **Orchestrator**: central brain handling task routing and validation (`legion/orchestrator.py`).
- **Agents**: implementations under `legion/agents/` with healthchecks and metrics.
- **UI**: Vite/React frontend in `ui/` with FastAPI backend in `interface/`.
- **State Repo**: persistent storage under `memory/` and database migration logic.
- **Ports**: documented in `LEGION_PORTS.md`.

## Test Failures
`pytest` not installed or tests not run.

## Hard-coded/Open Ports
:5001, :5555, :7803, :8000
Example entries:
legion/core/constants.py:8:PORT_ENV_PREFIX = "PORT_ALLOCATOR_"
legion/core/network.py:14:    url: str = "http://localhost:8000/", timeout: float = 2.0
legion/ports.py:37:        if value is not None and key.startswith("PORT_ALLOCATOR_"):
legion/ports.py:38:            service_name = key.replace("PORT_ALLOCATOR_", "").lower()
docker-compose.yml:24:      - "${PORT_ALLOCATOR_DEV_FRONTEND}:8000"
docker-compose.yml:26:      test: "curl -f http://web:7803/health || exit 1"
docker-compose.yml:29:      - PORT_ALLOCATOR_DEV_FRONTEND=8000
docker-compose.yml:31:      # - ORCHESTRATOR_ADDRESS=tcp://host.docker.internal:5555 # Example for Docker Desktop
docker-compose.yml:41:      - "${CHROMA_PORT:-20032}:8000"
ui/frontend/src/components/PortMapDisplay.jsx:7:    fetch('http://localhost:5001/ports')

## TODO/FIXME Hotspots
legion/core/db_utils.py:15:        # TODO: Execute schema.sql or define tables here
legion/core/db_utils.py:29:    # TODO: Implement basic migration logic
legion/orchestrator.py:1923:        # TODO: Fetch task details from StateManager or task queue
legion/orchestrator.py:1934:        # TODO: Fetch task list from StateManager with filters
legion/orchestrator.py:1946:        # TODO: Send cancellation request (e.g., update status, signal worker)
legion/orchestrator.py:1958:        # TODO: Implement actual agent start logic (e.g., process creation, state update)
legion/orchestrator.py:1966:        # TODO: Implement actual agent stop logic (e.g., signal process, state update)
legion/orchestrator.py:1974:        # TODO: Implement actual agent restart logic (stop then start)
legion/orchestrator.py:2086:            # TODO: This is a synchronous call to an agent that might be async.
legion/orchestrator.py:2138:        pass  # TODO: implement routing

Dependency analysis skipped due to missing network access.
See `port_scan.log` and `todo_scan.log` for full results.
