# Legion: Deployment & Troubleshooting

## Environment Variables (Strictly Required)
All scripts rely on environment variables. Failure to provide them is failure.

1.  **Source:** Use a `.env` file (copy `.env.example`) or set directly in your shell/CI environment.
2.  **Core Variables:**
    - `DISCORD_TOKEN`: Your Discord bot token.
    - `ORCH_CONFIG_PATH`: Path to the main orchestrator config (e.g., `legion/configs/orchestrator.yaml`).
    - `DISCORD_CHANNELS_PATH`: Path to the agent channel mapping file (e.g., `legion/configs/channels.yaml`).
    - *Add other critical variables here as needed.*

## Execution (Makefile is Law)
Use `make` for all standard operations:

- `make test`: Run full validation suite (lint, types, tests, structure checks).
- `make deploy`: Execute the deployment script (`scripts/deploy.sh`). Assumes tests passed.
- `make logs`: Tail recent logs from `scripts/logs/`.
- `make clean`: Obliterate logs in `scripts/logs/`.

**Context:** Run locally, on servers, or in CI/CD. Scripts validate environment variables and require execute permissions (`chmod +x scripts/*.sh`).

## CI/CD Pipeline (GitHub Flow Recommended)
Follows GitHub Flow principles [[Cite: GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)]:

1.  **Test Phase (on PR/Push):**
    - Install dependencies (`pip install -r requirements.txt`).
    - Make scripts executable (`chmod +x`).
    - Run `make test` (includes lint, types, unit, integration, performance, security checks).
    - Upload logs (`scripts/logs/`) as artifacts on failure.
2.  **Deploy Phase (on Merge to `main`, if tests pass):**
    - Install dependencies, ensure scripts are executable.
    - Run `make deploy`.
    - Upload logs on failure.

## Logs & Debugging
- **Location:** All operational logs reside in `scripts/logs/`.
- **Format:** Structured JSON (see `legion/core/logging_config.py`).
- **Access:** Use `make logs` or inspect files directly.
- **CI/CD:** Check build artifacts for logs on failure.

## Troubleshooting (Common Failures)
- **Missing Env Var:** Script will exit with error. Verify `.env` or environment setup.
- **Bot Startup Failure:** Check JSON logs in `scripts/logs/` for orchestrator or Discord API errors.
- **Test Failures:** Examine `scripts/logs/` for detailed pytest output and stack traces.
- **DB/Memory Issues:** Ensure `scripts/init_memory.sh` ran successfully. Check `memory/db/legion.db` existence and logs.
- **Permissions:** Run `chmod +x scripts/*.sh`.
- **Structure Compliance Failure:** Check CI logs for specific file/directory violations against `legion-structure` rules.

## Onboarding
1.  Clone the repository.
2.  Copy `.env.example` to `.env` and populate.
3.  Run `make test` to validate setup.
4.  Consult this guide, `README.md`, and `architecture.md`.

---
Submit PRs for documentation updates. Vague or incorrect docs will be rejected.
