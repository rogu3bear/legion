# Legion Architecture (2024 Edition)

## Grim System Overview
Legion is a modular, ruthlessly layered agent orchestration system. Every file, class, and function is mapped to a canonical logic layer. Any deviation is a CI failure and a personal affront to the architect.

## Logic Layers (Structure Compliance)

1. **Configuration Layer** (`legion/configs/`, `.env`)
   - YAML agent definitions, environment variables, channel IDs
2. **Orchestration Layer** (`legion/orchestrator.py`)
   - Loads configs, spins up agents, routes messages, schedules tasks
3. **Agent Layer** (`legion/agents/`)
   - Persona runtime code (Architect, Doctor, Researcher, etc.)
4. **Skill & Utility Layer** (`skills/`, `core/utils/`)
   - Search, summarization, networking, indexing, retry logic
5. **Persistence Layer** (`memory/`)
   - SQLite DB, memory API, JSONL logs
6. **Integration Layer** (`integration/discord/`)
   - Discord bot glue: cogs, settings, bot bootstrap
7. **Presentation Layer** (`interface/`)
   - FastAPI endpoints, front-end scripts, templates
8. **Infrastructure Layer** (`scripts/`, `.github/`, `docs/`, `changelog.md`)
   - CI, ops, migrations, changelog, docs

**Rule:** All required files and directories must exist. Any drift = CI failure.

---

## Dependency Injection (DI)
- All core services (`ILLMClient`, `IStateManager`, `IMemoryManager`) are injected via `legion/core/di_container.py`.
- Use `container.get()` or helpers like `get_llm_client()`.
- No hardcoded singletons. All agents and orchestrator receive dependencies via DI.

---

## Structured Logging & Error Boundaries
- All modules use `legion/core/logging_config.py` for JSON logs.
- Logs include timestamp, level, name, message, filename, function, and line.
- Error boundaries at every service boundary. All exceptions are logged with stack trace.
- Telemetry: LLM latency, dispatch duration, error counts.

---

## Testing & Validation
- **Unit Tests:** All service interfaces, agent logic, and utilities.
- **Integration Tests:** Orchestrator-agent flows, Discord bot, memory persistence.
- **Performance Tests:** LLM and orchestrator latency, throughput.
- **Security Tests:** Input validation, dangerous command rejection, privilege boundaries.
- **CI:** All tests, lint, type checks, and structure compliance enforced on every push.

---

## API & Module Reference

### Orchestrator (`legion/orchestrator.py`)
- `dispatch_message(agent_name, content, author=None, timestamp=None)` — Async. Routes message to agent, returns response.
- `submit_feedback(feedback: dict)` — Log feedback to state.
- `update_agent_config(agent_name, model, temperature, max_tokens)` — Hot-swap agent config.
- `get_state_key(key)` — Fetch value from orchestrator state.
- `add_alert_subscriber(user_id)` — Subscribe user to alerts.

### LLMClient (`legion/core/llm_client.py`)
- `generate(agent_name, thread_id, dynamic_rules, history, **override_kwargs)` — Generate LLM completion.

### BaseAgent (`legion/agents/base.py`)
- `handle_message(content, author, timestamp, context)` — Unified message handling pipeline.
- `post_to_discord(message)` — Post to Discord, split if too long.
- `self_assess()` — Run self-assessment, post result.

### StateManager (`legion/core/state.py`)
- `get_state()` — Get current state.
- `update_state(updates)` — Merge and persist state updates.
- `log_task(task)` — Append timestamped task entry.
- `log_error(error)` — Append error entry.
- `add_feedback(feedback)` — Log feedback.
- `get_recent_tasks(limit)` — Get recent tasks.
- `get_recent_errors(limit)` — Get recent errors.
- `log_telemetry(event)` — Log telemetry event.

### LegionAgentMemory (`memory/legion_memory.py`)
- `get(key)` / `set(key, value)` / `save()` — Key-value memory.
- `log_task(task)` / `get_task_log()` — Task logging.
- `save_document(name, content)` / `get_document(name, version)` — Versioned docs.
- `list_documents()` / `list_versions(name)` — Document management.
- `retrieve_memories(agent_name, embedding, top_k, base_dir)` — Vector search.
- `store_memories(agent_name, snippets, base_dir)` — Store vector memories.
- `add_raw_memory(text, metadata)` — Raw text memory.

### Core Utilities
- `health_check(url, timeout)` — HTTP 200 check.
- `fetch_with_retries(url, retries, timeout, backoff)` — HTTP GET with retries.
- `basic_health_check(url, timeout)` — Health check with status/elapsed.
- `build_inverted_index(docs, field)` — Inverted index builder.

### Skills
- `vector_search(query_embedding, docs, top_k)` — Cosine similarity search.
- `summarize_snippets(snippets, model, max_tokens, temperature)` — LLM-based summarization.

---

## Unified Agent Message Handling (No Prompt Drift)
- All agents use the same pipeline: config prompt → memory → thread history → LLM → Discord → memory.
- No per-agent prompt hacks. All flows are robust and error-tolerant.

---

## Security & Observability
- All dangerous commands are rejected and tested.
- All config changes, agent updates, and errors are logged.
- Bandit and security linters run in CI.
- Audit logging for sensitive actions.
- All logs are JSON, dyslexia-friendly, and Apple-grade.

---

## Structure Compliance (CI Death Sentence)
- All required files/dirs must exist. All stubs must have correct syntax.
- All imports must resolve. Any drift = CI failure and a warning in blood-red Comic Sans.

---

## Future-Proofing
- Horizontal scaling, distributed memory, and load balancing are on the roadmap.
- All new agents, skills, and endpoints must follow the above rules or face the void.
