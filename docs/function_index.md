# Function Index

| Path | Module/Class | Function | Signature | Summary |
| ---- | ------------ | -------- | --------- | ------- |
| `legion/core/db.py` | module | `init_db` | `init_db() -> None` | Initialize the Legion database (stub). |
| `legion/core/db.py` | module | `run_migrations` | `run_migrations() -> None` | Run database migrations (stub). |
| `legion/core/llm_client.py` | `LLMClient` | `__init__` | `(api_key: Optional[str] = None, model: Optional[str] = None, api_base: Optional[str] = None, **default_kwargs: Any) -> None` | Initialize the LLM client with optional API key, model, base URL, and defaults. |
| `legion/core/llm_client.py` | `LLMClient` | `generate` | `(agent_name: str, thread_id: str, dynamic_rules: Dict[str, Any], history: List[Dict[str, str]], **override_kwargs: Any) -> str` | Generate a completion using dynamic rules and conversation history. |
| `legion/core/network.py` | module | `placeholder_network` | `(url: str = "http://localhost:8000/", timeout: float = 2.0) -> dict` | Perform basic HTTP GET health check, return status and elapsed time. |
| `legion/core/network.py` | module | `health_check` | `(url: str, timeout: float = 2.0) -> bool` | HTTP GET, return True if status code == 200, else False. |
| `legion/core/network.py` | module | `fetch_with_retries` | `(url, retries: int = 3, timeout: float = 2.0, backoff: float = 0.5)` | HTTP GET with retry logic; returns successful response or raises last error. |
| `legion/core/indexing.py` | module | `placeholder_indexing` | `(docs: List[Dict], field: str = "text") -> Dict[str, List[int]]` | Build a simple inverted index mapping words to doc indices. |
| `legion/core/state.py` | `StateManager` | `__init__` | `(state_dir: str = "./memory/state") -> None` | Initialize state directory, files, and default config. |
| `legion/core/state.py` | `StateManager` | `_save_state` | `(state: Dict[str, Any]) -> None` | Save state object to JSON file. |
| `legion/core/state.py` | `StateManager` | `get_state` | `() -> Dict[str, Any]` | Load and return the current state. |
| `legion/core/state.py` | `StateManager` | `update_state` | `(updates: Dict[str, Any]) -> None` | Merge and persist state updates. |
| `legion/core/state.py` | `StateManager` | `log_task` | `(task: Dict[str, Any]) -> None` | Append a timestamped task entry to tasks log. |
| `legion/core/state.py` | `StateManager` | `log_error` | `(error: Dict[str, Any]) -> None` | Append a timestamped error entry to errors log. |
| `legion/core/state.py` | `StateManager` | `add_feedback` | `(feedback: Dict[str, Any]) -> None` | Append user feedback entry to feedback log. |
| `legion/core/state.py` | `StateManager` | `adjust_confidence_threshold` | `(new_threshold: float) -> None` | Update confidence threshold in config. |
| `legion/core/state.py` | `StateManager` | `get_recent_tasks` | `(limit: int = 100) -> List[Dict[str, Any]]` | Return most recent tasks from log, up to limit. |
| `legion/core/state.py` | `StateManager` | `get_recent_errors` | `(limit: int = 100) -> List[Dict[str, Any]]` | Return most recent errors from log, up to limit. |
| `legion/core/init_memory.py` | module | `main` | `() -> None` | Create the memory database file if missing. |
| `legion/core/prompt_builder.py` | `PromptBuilder` | `build` | `(system_prompt: str, memories: List[str], thread_history: List[Dict[str, str]], user_query: str, memory_prefix: str = "Previously on our project:", reflection_prompt: str = "Reflection: think step-by-step before answering.") -> List[Dict[str, str]]` | Construct LLM messages list from prompt, memories, history, and user query. |
| `legion/orchestrator.py` | `Orchestrator` | `__init__` | `(post_agent_message=None, pid_file=None, state_manager=None, llm_client=None) -> None` | Initialize orchestrator: locking, config loading, agent instantiation, state. |
| `legion/orchestrator.py` | `Orchestrator` | `_acquire_lock` | `() -> None` | Acquire filesystem lock for a single orchestrator instance. |
| `legion/orchestrator.py` | `Orchestrator` | `_release_lock` | `() -> None` | Release the orchestrator filesystem lock. |
| `legion/orchestrator.py` | `Orchestrator` | `_setup_signal_handlers` | `() -> None` | Register OS signal handlers for graceful shutdown. |
| `legion/orchestrator.py` | `Orchestrator` | `handle_signal` | `(signum: int, frame) -> None` | Internal handler to respond to OS signals. |
| `legion/orchestrator.py` | `Orchestrator` | `_get_channel_id` | `(agent_name: str) -> int` | Lookup Discord channel ID for an agent. |
| `legion/orchestrator.py` | `Orchestrator` | `load_agent_configs` | `() -> Dict[str, Any]` | Load agent YAML configuration files. |
| `legion/orchestrator.py` | `Orchestrator` | `register_test_agents` | `() -> None` | Register dummy agents for test environment. |
| `legion/orchestrator.py` | `Orchestrator` | `run_once` | `(event=None) -> List[Dict[str, Any]]` | Execute a single orchestrator cycle, returning events. |
| `legion/orchestrator.py` | `Orchestrator` | `run` | `(interval: int = 5) -> None` | Loop `run_once` every `interval` seconds. |
| `legion/orchestrator.py` | `Orchestrator` | `agent_registry` | `property -> Dict[str, Callable]` | Mapping of agent names to their classes. |
| `legion/orchestrator.py` | `Orchestrator` | `get_agent_channel` | `(agent_name: str) -> int` | Get the Discord channel ID for a specific agent. |
| `legion/orchestrator.py` | `Orchestrator` | `ask` | `(agent_name: str, prompt: str, context=None) -> str` | Send a prompt to an agent and return its response. |
| `legion/orchestrator.py` | `Orchestrator` | `broadcast` | `(prompt: str) -> None` | Broadcast a prompt message to all agents. |
| `legion/orchestrator.py` | `Orchestrator` | `post_update` | `(agent_name: str, content: str, files=None) -> None` | Post update content on behalf of an agent. |
| `legion/orchestrator.py` | `Orchestrator` | `comment_on_post` | `(agent_name: str, target_agent: str, comment: str) -> None` | Comment on another agent's post. |
| `legion/orchestrator.py` | `Orchestrator` | `react_to_post` | `(agent_name: str, target_agent: str, emoji: str) -> None` | React to another agent's post with an emoji. |
| `legion/orchestrator.py` | `Orchestrator` | `request_assistance` | `(agent_name: str, issue: str) -> None` | Request assistance for a given issue. |
| `legion/orchestrator.py` | `Orchestrator` | `self_assess` | `(agent_name: str) -> None` | Trigger a self‑assessment for a single agent. |
| `legion/orchestrator.py` | `Orchestrator` | `assess_all_agents` | `() -> None` | Run self‑assessment for all agents. |
| `legion/orchestrator.py` | `Orchestrator` | `notify_agent` | `(agent_name: str, message: str) -> None` | Send a notification to an agent's channel. |
| `legion/orchestrator.py` | `Orchestrator` | `send_message` | `(from_agent: str, to_agent: str, payload: dict) -> None` | Send a payload from one agent to another. |
| `legion/orchestrator.py` | `Orchestrator` | `deliver_message` | `(to_agent: str, payload: dict) -> None` | Deliver a payload to an agent immediately. |
| `legion/orchestrator.py` | `Orchestrator` | `load_yaml` | `(path: str) -> Any` | Read and parse a YAML file. |
| `legion/orchestrator.py` | `Orchestrator` | `dispatch_message` | `(agent_name: str, content: str, author: str = None, timestamp: str = None) -> str` | Dispatch user message to agent and return response. |
| `legion/orchestrator.py` | `Orchestrator` | `run_self_assess_all` | `async() -> None` | Helper to invoke `self_assess` on all agents in background. |
| `legion/orchestrator.py` | `Orchestrator` | `reload_agent_configs` | `(llm_client=None) -> Dict[str, Any]` | Reload agent configs and update instances. |
| `legion/orchestrator.py` | `Orchestrator` | `submit_feedback` | `(feedback: dict) -> None` | Record user feedback via state manager. |
| `legion/orchestrator.py` | `Orchestrator` | `update_agent_config` | `(agent_name: str, model: str, temperature: float, max_tokens: int) -> None` | Update agent's runtime settings. |
| `legion/orchestrator.py` | `Orchestrator` | `get_state_key` | `(key: str) -> object` | Retrieve a value from orchestrator state. |
| `legion/orchestrator.py` | `Orchestrator` | `add_alert_subscriber` | `(user_id: int) -> None` | Subscribe a user to receive critical alerts. |
| `legion/orchestrator.py` | `Orchestrator` | `get_alert_subscribers` | `() -> set` | Return all subscribed user IDs for alerts. |

## Missing Docstrings / Unclear Purpose

The following methods lack docstrings or have unclear intent:

- `legion/orchestrator.py`: `_get_channel_id`, `register_test_agents`
- `legion/agents/base.py`: `loop`

## Functional Areas Overview

- **Orchestration** (`legion/orchestrator.py`): agent lifecycle, messaging, locking, config
- **Agents** (`legion/agents/...` & `memory/legion_memory.py`): core agent logic, memory, LLM integration
- **Core Utilities** (`legion/core/`): LLM client, state management, networking, indexing, prompt building, DB stubs
- **Integration** (`integration/discord/`): Discord bot and command cogs
- **Presentation** (`interface/`): FastAPI endpoints, WebSocket feed, static UI
- **Skills** (`skills/`): placeholder search and summarization logic

### Grouping & Naming Suggestions

- Consolidate all low‑level helpers (`network`, `indexing`, `prompt_builder`) under `legion/core/utils.py` for clarity.
- Rename ambiguous orchestrator internals (`_get_channel_id`, `loop`) to more descriptive names.
- Consider grouping agent testing stubs (`register_test_agents`) into a separate testing utility module.
