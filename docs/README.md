# Legion: Project Overview

## Mandate
Legion is a modular agent orchestration system built on a canonical layered architecture. Non-compliance is not an option; CI enforces the structure.

**Core Documents:**
- [Legion Architecture](architecture.md): System design, APIs, layers, rules.
- [Deployment Guide](DEPLOYMENT.md): Environment setup, scripts, CI/CD, troubleshooting.
- [Changelog](changelog.md): History of all notable changes.

## Structure & Layers
Refer to [Legion Architecture](architecture.md) for the definitive 8-layer model. All files and directories MUST conform.

## Environment Setup
1.  **Create `.env`**: Copy `.env.example` to `.env`.
2.  **Populate Secrets**: Fill in required values (e.g., `DISCORD_TOKEN`, channel IDs).
    ```dotenv
    # Required:
    DISCORD_TOKEN=
    # Example Channel IDs (adjust for your server):
    GENERAL_CHANNEL_ID=
    AGENT_FEED_CHANNEL_ID=
    # ... other agent channel IDs as needed ...
    ```
3.  **Dependencies**: Use a Python virtual environment.
    ```bash
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    ```

## Getting Started / Local Run
Execute from the project root:

```bash
# Grant execution permissions & initialize memory (DB/logs)
chmod +x scripts/*.sh
./scripts/init_memory.sh

# Start the Discord bot (uses orchestrator)
./scripts/start_bot.sh
```

**Troubleshooting:** Check `.env`, dependencies, and the [Deployment Guide](DEPLOYMENT.md).

## Contribution Workflow (GitHub Flow)
Legion adheres to GitHub Flow for development [[Cite: GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)]:

1.  **Branch:** Create a descriptive branch (`feature/add-new-skill`, `fix/orchestrator-lock`).
2.  **Commit:** Make small, atomic commits with clear messages (`refactor: simplify network retries`, `feat: add summarization skill`).
3.  **Push:** Push changes regularly to your branch.
4.  **Pull Request (PR):** Open a PR against the `main` branch.
    *   Clearly describe the changes and the problem solved.
    *   Link related issues (e.g., `Closes #123`).
    *   Request reviews from relevant teams/individuals.
5.  **Review & Address:** Respond to feedback, push follow-up commits to the same branch.
6.  **Merge:** Once approved and CI checks pass, merge the PR.
7.  **Delete Branch:** Remove the merged feature branch.

**Branch Protection:** The `main` branch is likely protected, requiring reviews and passing CI checks before merging [[Cite: Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)].

## Key Features & Concepts
- **Unified Agent Handling:** See [Architecture Doc](architecture.md#unified-agent-message-handling-no-prompt-drift) for details.
- **Dependency Injection:** Core services are injected; see [Architecture Doc](architecture.md#dependency-injection-di).
- **Structured Logging:** JSON logs via `legion/core/logging_config.py`; see [Architecture Doc](architecture.md#structured-logging--error-boundaries).
- **Configuration Warnings:** Unknown keys in agent YAMLs are logged and ignored.

## Agent Roles and Capabilities
Legion employs a variety of specialized agents, each designed for specific tasks and possessing unique capabilities. The primary roles include:
- **Architect:** Oversees system design, plans new features, and ensures architectural integrity.
- **Developer:** Writes, tests, and debugs code for various components of Legion.
- **Researcher:** Gathers information, analyzes data, and provides insights for decision-making.
- **Doctor:** Monitors system health, diagnoses issues, and can perform corrective actions.
- **Other specialized agents:** Ping, Echo, Healthcheck for diagnostics and basic interactions.
(More details on specific agent capabilities can be found in their respective configuration files and agent layer code.)

## UI Tagging and Task Ownership
The Legion web interface provides visibility into agent status, including assigned tags and task ownership.
- **Tags:** Agents can be associated with various tags (e.g., `critical`, `ui`, `backend`, `data-processing`) which are displayed as colored chips in the UI. This allows for quick visual identification and filtering.
- **Task Owner:** If an agent is currently assigned to or working on a task initiated by a user or another process, the `task_owner` field will indicate the originator.

**Demo of UI Tagging:**
[View Tag UI Demo (GIF)](assets/demos/tag-ui-0517.gif) (Note: Ensure `assets/demos/tag-ui-0517.gif` is present)

## Port Mapping and Configuration
Legion services use a defined set of network ports for communication. These are managed centrally to avoid conflicts.
- **Configuration:** Port assignments are primarily defined in the `.env.ports` file at the project root. This file is loaded by services that require port information, such as the Vite frontend server and backend services.
- **Key Ports (Defaults, check `.env.ports` for current values):
  - `PORT_ALLOCATOR_UI_FRONTEND` (e.g., 7802): Used by the Vite/React frontend development server.
  - `PORT_ALLOCATOR_UI_BACKEND` (e.g., 7801): Used by the FastAPI backend that serves the API for the UI.
  - Other ports are defined for orchestrator, database, messaging, etc.
  - **Reference:** The `ui/frontend/vite.config.js` shows an example of how the frontend port is consumed. The FastAPI application entry point is `backend/main.py` (currently located at `interface/main.py`) and uses the port defined for the UI backend.

## Repository Topics
This repository uses topics for discoverability. Key topics might include: `agent-orchestration`, `discord-bot`, `python`, `llm`, `modular-architecture`. [[Cite: Topics](https://docs.github.com/articles/classifying-your-repository-with-topics)]

## Recent Updates
See [Changelog](changelog.md) for the full history.
