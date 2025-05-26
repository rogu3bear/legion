# Contributing to Legion

Thank you for considering contributing to Legion! We value community contributions and aim to maintain a high standard of code quality and collaboration.

## Development Setup
- Clone and run `make doctor`
- Start with `make dev` (port 7602)
- Python 3.12, Redis @ 7600, Node 18+

### Code Quality & Linting

*   **Python**: We use `flake8` and `black` for linting and formatting. These are typically run via `make lint` or pre-commit hooks.
*   **Frontend**: ESLint and Prettier are used for the frontend code. Run `pnpm --prefix ui/frontend run lint` and `pnpm --prefix ui/frontend run format` (or similar scripts defined in `ui/frontend/package.json`).
*   **Pre-commit Hooks**: It is highly recommended to install and use pre-commit hooks to automatically check and format your code before committing.
    ```bash
    pip install pre-commit
    pre-commit install
    ```

## Testing
- Run: `pnpm run test:coverage` (from `ui/frontend` directory)
- CI enforces 80% min lines/statements

## Branching
- PR required, green CI
- Use `feat/`, `fix/`, `chore/` prefixes

## Commit Message Style

We follow the **Conventional Commits** specification. This makes commit history more readable and helps automate changelog generation.

The basic format is:

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

*   **Type**: Must be one of the following: `feat`, `fix`, `build`, `chore`, `ci`, `docs`, `perf`, `refactor`, `revert`, `style`, `test`.
*   **Scope (optional)**: A noun describing the section of the codebase affected (e.g., `orchestrator`, `ui-feed`, `agent-memory`).
*   **Subject**: A short, imperative mood description of the change (e.g., `add prompt versioning API`, `correct user login flow`).

**Example:**
`feat(api): add endpoint for agent status`
`fix(ui): resolve incorrect display of timestamps`
`docs(contributing): clarify commit style guidelines`
`chore(deps): upgrade react to v18`

### Agent Instantiation Guard

*   Do not import or call agent classes directly (e.g., `ArchitectAgent(...)`).
*   Use `orchestrator.load_agent('<agent_key>')` to obtain agent instances.
*   The "Guard direct agent instantiation" pre-commit hook will run on commit to catch violations.
*   CI also enforces this via the `agent-instantiation-guard` job.

### Test Hygiene (Existing Guidelines)

*   Mark legacy or broken tests with:
    ```python
    import unittest
    @unittest.skip("legacy failure – deferred")
    class LegacyPlaceHolder(unittest.TestCase):
        pass
    ```
*   For missing dependencies in tests, extend `tests/compat_stubs.py` with:
    ```python
    import sys, types
    for name in ("openai", "discord", "discord.ext", "pytest"):
        sys.modules[name] = types.ModuleType(name)
    ```
*   Failing legacy tests should be quarantined by decorating test classes with `mark_legacy` from `tests.legacy_skip`.

## No Docker
- Docker is forbidden. Redis must be native.

## Questions or Issues?

If you have questions or run into issues, please open an issue on GitHub.

---
*This document was last updated: {{ CURRENT_DATE }}*
