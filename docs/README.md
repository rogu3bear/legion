# Legion

Modular agent orchestration system.

## Logic Layer System

Legion is organized into eight distinct logic layers:

1. **Configuration Layer**
   - YAML agent definitions and `.env` variables (prompts, schedules, channel IDs)
   - Location: `legion/configs/`, `.env`
2. **Orchestration Layer**
   - The "brain" that loads configs, spins up agents, routes messages, and schedules tasks
   - Location: `legion/orchestrator.py`
3. **Agent Layer**
   - Persona runtime code (Architect, Doctor, Researcher, Ping, Echo, Healthcheck, etc.)
   - Location: `legion/agents/`
4. **Skill & Utility Layer**
   - Reusable helpers: search engines, summarizers, networking, indexing, retry logic
   - Location: `skills/`, `core/utils/`
5. **Persistence Layer**
   - Persistent state: SQLite DB, memory API, JSONL logs
   - Location: `memory/`
6. **Integration Layer**
   - Discord-bot glue: cogs, settings, bot bootstrap
   - Location: `integration/discord/`
7. **Presentation Layer**
   - Web UI: FastAPI endpoints, front-end scripts, templates
   - Location: `interface/`
8. **Infrastructure Layer**
   - Ops-focused tooling: scripts, CI workflows, migrations, changelog, docs
   - Location: `scripts/`, `.github/`, `docs/`, `changelog.md`, etc.

---

## Environment Setup

Add the following to your `.env` file:

```dotenv
DISCORD_TOKEN=
GENERAL_CHANNEL_ID=
AGENT_FEED_CHANNEL_ID=
ARCHITECT_CHANNEL_ID=
METRICS_CHANNEL_ID=
THERAPIST_CHANNEL_ID=
DESIGN_CHANNEL_ID=
```

Legion reads all channel IDs from these vars—make sure they match your Discord server.

## Getting Started

- Use a **monospaced font** for all code.
- Run each step from your project root:

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
chmod +x scripts/*.sh && scripts/init_memory.sh
scripts/start_bot.sh
```

- If you see errors, check your `.env` and dependencies.
- For help, see the docs or run `scripts/verify_discord.sh`. 