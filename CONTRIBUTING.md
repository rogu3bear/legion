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
