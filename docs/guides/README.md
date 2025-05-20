# Developer Guide
Local setup, pre-commit hooks, VS Code settings.  
Extended tips: ../legacy/guides/
=======

1. Clone the repository and create a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Initialize memory stores with `./scripts/init_memory.sh`.
3. Start services in development mode using `make dev`.
4. Run `make lint` and `make test` before committing changes.
5. Follow GitHub Flow: branch from `main`, commit small logical units, and open a pull request.

For community guidelines and detailed contribution steps, consult the legacy docs.
👉 More: legacy/guides/*
