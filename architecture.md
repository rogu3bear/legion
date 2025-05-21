# Legion Architecture Report

## Snapshot
- **Commit**: 6943599820cf5c1b7caa0e51e371ca6888043e87
- **Date**: 2025-05-20 19:30:31 -0500

## High-level Module Map
- **Orchestrator** – located under `legion/orchestrator.py`. Manages message routing, API routes, and ZMQ PUB/SUB hooks.
- **Agents** – implementations live in `legion/agents/` and subfolders. Includes specialized agents such as Therapist, Architect, Echo and more.
- **State Repo** – database and migrations under `memory/db/` and `interface/migrations`. Uses SQLAlchemy models defined in `interface/models` with Alembic migrations.
- **UI Layers** – Flask/FastAPI backend in `interface/` and React frontend in `ui/`. Default ports configured via `legion/default_ports.py`.
- **Support Packages** – metrics collection (`metrics/`), middleware (`middleware/src`), and utilities under `core/utils`.

## Inter-service Port Table
Service | Port | Variable | Files
--- | --- | --- | ---
UI Backend | 7801 | `PORT_ALLOCATOR_UI_BACKEND` | `legion/default_ports.py`, `LEGION_PORTS.md`
UI Frontend | 7802 | `PORT_ALLOCATOR_UI_FRONTEND` | `legion/default_ports.py`, `LEGION_PORTS.md`
Orchestrator REST | 7803 | `PORT_ALLOCATOR_ORCHESTRATOR` | `legion/default_ports.py`, `LEGION_PORTS.md`
Interface API | 7804 | `PORT_ALLOCATOR_INTERFACE_API` | `legion/default_ports.py`, `LEGION_PORTS.md`
Middleware | 7805 | `PORT_ALLOCATOR_MIDDLEWARE` | `legion/default_ports.py`, `LEGION_PORTS.md`
Metrics | 7806 | `PORT_ALLOCATOR_METRICS` | `legion/default_ports.py`, `LEGION_PORTS.md`
Researcher API | 7807 | `PORT_ALLOCATOR_RESEARCHER_API` | `legion/default_ports.py`, `LEGION_PORTS.md`
ZMQ PUB | 7808 | `PORT_ALLOCATOR_ZMQ_PUB` | `legion/default_ports.py`, `LEGION_PORTS.md`
ZMQ SUB | 7809 | `PORT_ALLOCATOR_ZMQ_SUB` | `legion/default_ports.py`, `LEGION_PORTS.md`
Redis | 7810 | `PORT_ALLOCATOR_REDIS` | `legion/default_ports.py`, `LEGION_PORTS.md`

The repo has several hard-coded references to these ports. See `check_ports.py` and `generated/port_usage.json`.

## Dependency & Security Snapshot
- **Package list**:
  - Output from `pip list` shows packages like `fastapi 0.97.0`, `mypy 1.15.0`, `ruff 0.11.10`.
- **pipdeptree** and **safety** scans could not run due to network restrictions.

## Test-suite Baseline
- The repository contains roughly `60` test files with over `200` test cases but `pytest` could not be installed in this environment. No tests were executed.

## Coverage Gaps
- Coverage information unavailable because tests did not run.

## TODO / FIXME Hotspots
- Many TODOs across middleware and orchestrator modules (`middleware/src/main.py`, `legion/orchestrator.py`) and docs (e.g., `docs/orchestrator.md`).

## Immediate Risks
- Missing dependency management for `pytest`, `pipdeptree`, and `safety` prevents running tests and security scans offline.
- Several TODO sections indicate incomplete implementations in core services.

## Suggested Next Patches
- Add offline installation support for developer tooling (`pipdeptree`, `safety`, `pytest`).
- Refactor port constants to consistently use `PORT_ALLOCATOR_*` variables.
- Address TODOs in `middleware/src/main.py` and `legion/orchestrator.py` for stable agent dispatch.
- Review documentation to ensure port ranges align with `LEGION_PORTS.md`.
