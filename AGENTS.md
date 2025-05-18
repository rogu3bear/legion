# AGENTS Guidelines

This repository manages Legion, an agent orchestration system. The following conventions apply to all contributions.

## Repository Structure
- **Backend**: `interface/` directory (scheduled to be renamed `backend/`).
- **Frontend**: `ui/frontend/` directory (scheduled to be renamed `frontend/`).
- **Documentation**: `docs/` directory at the repo root.

## Development Workflow
1. Ensure `ruff`, `mypy`, and `eslint` run clean. In restricted environments where tools or dependencies are unavailable, perform static analysis and document any issues.
2. Run `make lint` and `make test` before committing. If commands fail due to missing dependencies, outline the expected results in the PR description. Tests are located in `tests/`.
3. New features must include doc updates and minimal, deterministic tests.
4. Ports are defined via `.env.ports`; do not hard-code port numbers or secrets.

## Coding Style
- Python 3.11+, four-space indentation, line length 88.
- Use grouped and alphabetically sorted imports.
- Provide docstrings for all public functions and classes.

## Pull Requests
- Summaries should highlight documentation changes and any structural updates.
- Include a brief testing section describing lint and test results.


## Dependency Management
- Python dependencies are listed in `requirements.txt`. Node dependencies for the React frontend live in `ui/frontend/package.json`.
- If runtime package installation is not possible, update these files based on static inspection and ensure configuration files (`package-lock.json`, `.ruff.toml`, `mypy.ini`) are kept in sync.
