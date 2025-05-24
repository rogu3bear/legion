# Contributing

## Code Quality

### Pre-commit Setup

**Required for all contributors:**
```bash
pre-commit install
```

This enables automatic checks on every commit including:
- Agent instantiation guard
- Type debt regression guard  
- Code formatting and linting

### Agent Instantiation Guard

- Do not import or call agent classes directly (e.g., `ArchitectAgent(...)`).
- Use `orchestrator.load_agent('<agent_key>')` to obtain agent instance.
- CI enforces this via the `agent-instantiation-guard` job in `.github/workflows/ci.yml`.

### Type Debt Management

**Zero-regression policy:** New code cannot increase mypy error count.

- **Current baseline:** 90 type errors
- **Check status:** `python tools/type_debt.py`
- **Fix errors:** Focus on files with ≤3 errors for quick wins
- **Progress tracking:** Automatic Discord notifications on changes

**Guidelines:**
- Add type annotations to new functions
- Use `# type: ignore[specific-error]` for unavoidable issues
- For files with >10 errors, add `# mypy: ignore-errors` header
- PRs that reduce debt get auto-labeled `typing-reduction` 🏆

Run `pnpm i` in `ui/frontend` to enable ESLint locally.

## Test Hygiene

- Mark legacy or broken tests with:

  ```python
  import unittest
  @unittest.skip("legacy failure – deferred")
  class LegacyPlaceHolder(unittest.TestCase):
      pass
  ```

- For missing dependencies in tests, extend `tests/compat_stubs.py` with:

  ```python
  import sys, types
  for name in ("openai", "discord", "discord.ext", "pytest"):
      sys.modules[name] = types.ModuleType(name)
  ```

## Legacy Tests
Failing legacy tests should be quarantined by decorating test classes with
`mark_legacy` from `tests.legacy_skip`:

```python
from tests.legacy_skip import mark_legacy

@mark_legacy
class LegacyPlaceHolder(unittest.TestCase):
    ...
```

Record quarantined files in `docs/TODO.md` under **Legacy Tests (quarantined)**.

## Smoke Test
Run the integration smoke test with:

```bash
python scripts/integration_smoke.py
```
