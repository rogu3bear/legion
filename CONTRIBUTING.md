# Contributing

## Code Quality

### Agent Instantiation Guard

- Do not import or call agent classes directly (e.g., `ArchitectAgent(...)`).
- Use `orchestrator.load_agent('<agent_key>')` to obtain agent instances.
- Ensure you have `pre-commit` installed and run:
  ```bash
  pre-commit install
  ```
- The "Guard direct agent instantiation" hook will run on commit to catch violations.
- CI also enforces this via the `agent-instantiation-guard` job in `.github/workflows/ci.yml`.
- Run `pnpm i` in `ui/frontend` to enable ESLint locally.

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
