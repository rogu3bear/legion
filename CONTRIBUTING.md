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
