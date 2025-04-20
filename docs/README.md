# Legion

Modular agent orchestration system.

## Logic Layer System

Legion is organized into eight distinct logic layers:

1. **Configuration Layer**
   - YAML agent definitions and environment variables (prompts, schedules, channel IDs)
   - Location: configuration module
2. **Orchestration Layer**
   - The "brain" that loads configs, spins up agents, routes messages, and schedules tasks
   - Location: orchestration module
3. **Agent Layer**
   - Persona runtime code (Architect, Doctor, Researcher, Ping, Echo, Healthcheck, etc.)
   - Location: agent modules
4. **Skill & Utility Layer**
   - Reusable helpers: search engines, summarizers, networking, indexing, retry logic
   - Location: skills and utility modules
5. **Persistence Layer**
   - Persistent state: database, memory API, logs
   - Location: memory module
6. **Integration Layer**
   - Discord-bot glue: cogs, settings, bot bootstrap
   - Location: integration module
7. **Presentation Layer**
   - Web UI: API endpoints, front-end scripts, templates
   - Location: interface module
8. **Infrastructure Layer**
   - Ops-focused tooling: scripts, CI workflows, migrations, changelog, docs
   - Location: infrastructure modules

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
./scripts/start_bot.sh
```

- If you see errors, check your `.env` and dependencies.
- For help, see the documentation or run the Discord integration verification script.

## Unified Agent Message Handling

All Legion agents now inherit a single, unified message handling pipeline from `BaseAgent`. This pipeline:

1. Loads the agent's default prompt from its config (with a safe fallback).
2. Retrieves top-K relevant memory snippets using the memory module's index helper.
3. Fetches the last N messages from the Discord thread for context.
4. Builds the LLM payload in this order:
   - System message with the default prompt
   - System message summarizing retrieved memories (or a fallback if none)
   - The thread history messages (user/assistant)
   - The new user message
5. Sends the payload to the LLM and posts the reply back to Discord.
6. Extracts and stores new memory items from the assistant's reply.

No agent-specific prompt orchestration remains—every agent uses this robust, error-tolerant flow.

## Developer Guide

See [Developer Guide](developer_guide.md) for a full end-to-end flow diagram, helper documentation, and error handling details. 