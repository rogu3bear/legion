# AGENTS Guidelines

This repository manages Legion, an agent orchestration system. The following conventions apply to all contributions.

## Repository Structure
- **Backend**: `interface/` directory (scheduled to be renamed `backend/`).
- **Frontend**: `ui/frontend/` directory (scheduled to be renamed `frontend/`).
- **Documentation**: `docs/` directory at the repo root.

## Development Workflow
1. Ensure `ruff`, `mypy`, and `eslint` run clean.
2. Run `make lint` and `make test` before committing. Tests are located in `tests/`.
3. New features must include doc updates and minimal, deterministic tests.
4. Ports are defined via `.env.ports`; do not hard-code port numbers or secrets.

## Coding Style
- Python 3.11+, four-space indentation, line length 88.
- Use grouped and alphabetically sorted imports.
- Provide docstrings for all public functions and classes.

## Pull Requests
- Summaries should highlight documentation changes and any structural updates.
- Include a brief testing section describing lint and test results.

