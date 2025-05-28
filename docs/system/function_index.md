<!-- File: docs/system/function_index.md -->

| Path | Module/Class | Function | Signature | Summary |
|------|-------------|----------|-----------|---------|
| legion/core/utils/chroma_client.py | AsyncChromaClient | __init__ | (self, api_url, api_key) | Needs Documentation |
| legion/core/utils/chroma_client.py | AsyncChromaClient | __setattr__ | (self, name, value) | Needs Documentation |
| legion/core/utils/chroma_client.py | AsyncChromaClient | delete_by_id | (self, agent_name, interaction_id) | Needs Documentation |
| legion/core/utils/chroma_client.py | AsyncChromaClient | get_collection_stub | (name_arg) | Needs Documentation |
| legion/core/utils/chroma_client.py | AsyncChromaClient | query_similar | (self, agent_name, embedding, n_results) | Needs Documentation |
| legion/core/utils/chroma_client.py | AsyncChromaClient | upsert_batch | (self, records) | Needs Documentation |
| legion/core/utils/chroma_client.py | AsyncChromaClient | upsert_embedding | (self, record) | Needs Documentation |
| integration/discord/bot.py | - | fetch_thread_history | (channel, thread, limit) | Fetch up to `limit` messages from the given thread (or channel). |
| integration/discord/bot.py | - | main | () | Main entry point for the Discord bot. |
| integration/discord/bot.py | - | run_self_assess_all | (orchestrator) | Needs Documentation |
| integration/discord/bot.py | LegionBot | __init__ | (self, orchestrator, *args, **kwargs) | Needs Documentation |
| integration/discord/bot.py | LegionBot | _handle_signal | (self, sig) | Handle shutdown signals gracefully. |
| integration/discord/bot.py | LegionBot | _schedule_maintenance | (self) | Schedule periodic maintenance tasks. |
| integration/discord/bot.py | LegionBot | _send_agent_message | (self, agent, payload) | Send a message to an agent's Discord channel. |
| integration/discord/bot.py | LegionBot | on_message | (self, message) | Needs Documentation |
| integration/discord/bot.py | LegionBot | on_ready | (self) | Needs Documentation |
| integration/discord/bot.py | LegionBot | setup_hook | (self) | Needs Documentation |
| integration/discord/cogs/health.py | HealthcheckAgent | __init__ | (self, name, config, channel) | Initializes healthcheck agent and records start time. |
| integration/discord/cogs/health.py | HealthcheckAgent | _health_loop | (self) | Periodically checks uptime and logs health status. |
| integration/discord/cogs/health.py | HealthcheckAgent | start | (self) | Starts the health check loop. |
| integration/discord/cogs/orchestrator.py | - | setup | (bot) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | __init__ | (self, bot, orchestrator) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | ask | (self, interaction, agent_name, question) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | echo | (self, interaction, message) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | healthcheck | (self, interaction) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | llm_test | (self, interaction) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | metrics_report | (self, interaction) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | reload_configs | (self, interaction) | Slash command to reload agent configurations at runtime. |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | review | (self, interaction) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | sync_call | () | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | update_config | (self, interaction, agent_id, key, value) | Needs Documentation |
| integration/discord/cogs/orchestrator.py | OrchestratorCog | ux_critique | (self, interaction) | Needs Documentation |
| integration/discord/cogs/ux_feed.py | - | render_error | (agent_name, error_msg, details) | Creates an error message embed. |
| integration/discord/cogs/ux_feed.py | - | render_feed_item | (agent_name, message, msg_type, fields) | Creates a Discord embed for an agent message. |
| integration/discord/cogs/ux_feed.py | - | render_info | (agent_name, message, fields) | Creates an info message embed. |
| integration/discord/cogs/ux_feed.py | - | render_message | (agent_name, message, fields) | Alias for render_info for general message rendering. |
| integration/discord/cogs/ux_feed.py | - | render_success | (agent_name, message, metrics) | Creates a success message embed. |
| integration/discord/cogs/ux_feed.py | - | render_warning | (agent_name, message, fields) | Creates a warning message embed. |
| interface/api/v1/endpoints/agents.py | - | create_agent_db | (agent_data, current_user, db) | Create a new agent in the database (superuser only). |
| interface/api/v1/endpoints/agents.py | - | delete_agent_db | (agent_id, current_user, db) | Delete an agent by its ID (superuser only). |
| interface/api/v1/endpoints/agents.py | - | dispatch_message_to_agent | (agent_name, payload, current_user) | Sends a message or command to a specific agent via the Orchestrator. |
| interface/api/v1/endpoints/agents.py | - | get_agent_configuration | (agent_name, current_user) | Retrieves the current configuration for a specific agent. |
| interface/api/v1/endpoints/agents.py | - | get_agent_db | (agent_id, current_user, db) | Retrieve an agent by its ID. |
| interface/api/v1/endpoints/agents.py | - | get_agent_status | (agent_name, current_user) | Retrieves the detailed status for a specific agent. |
| interface/api/v1/endpoints/agents.py | - | list_agent_capabilities | (current_user) | Return mapping of agents to their capability methods. |
| interface/api/v1/endpoints/agents.py | - | list_agents | (current_user) | Retrieves a list of all registered agents and their current status. |
| interface/api/v1/endpoints/agents.py | - | reload_all_agents_configs | (current_user) | Triggers a reload of all agent configurations via the Orchestrator. |
| interface/api/v1/endpoints/agents.py | - | restart_agent | (agent_name, current_user) | Sends a command to the Orchestrator to restart a specific agent. |
| interface/api/v1/endpoints/agents.py | - | start_agent | (agent_name, current_user) | Sends a command to the Orchestrator to start a specific agent. |
| interface/api/v1/endpoints/agents.py | - | stop_agent | (agent_name, current_user) | Sends a command to the Orchestrator to stop a specific agent. |
| interface/api/v1/endpoints/agents.py | - | trigger_agent_assessment | (agent_name, current_user) | Triggers a self-assessment process for a specific agent. |
| interface/api/v1/endpoints/agents.py | - | update_agent_configuration | (agent_name, config_data, current_user) | Updates the configuration for a specific agent via the Orchestrator. |
| interface/api/v1/endpoints/agents.py | - | update_agent_db | (agent_id, agent_data, current_user, db) | Update an existing agent (superuser only). |
| interface/api/v1/endpoints/auth.py | - | get_user_preferences | (current_user, db) | Retrieves the preferences for the currently authenticated user. |
| interface/api/v1/endpoints/auth.py | - | login_for_access_token | (db, form_data) | Authenticates a user using username and password (OAuth2 password flow). |
| interface/api/v1/endpoints/auth.py | - | logout | (current_user) | Logs the currently authenticated user out. |
| interface/api/v1/endpoints/auth.py | - | read_users_me | (current_user) | Retrieves the details of the currently authenticated user. |
| interface/api/v1/endpoints/auth.py | - | register_user | (user_in, db) | Registers a new user in the system. |
| interface/api/v1/endpoints/auth.py | - | update_user_preferences | (preferences_in, current_user, db) | Updates the preferences for the currently authenticated user. |
| interface/api/v1/endpoints/login.py | - | login_access_token | (db, form_data) | Authenticate user and return access token. |
| interface/api/v1/endpoints/memory.py | - | get_memory_document | (doc_name, version, current_user) | Retrieves a specific document (optionally a specific version) from the [...] |
| interface/api/v1/endpoints/memory.py | - | list_memory_documents | (current_user) | Retrieves a list of document names stored in the Legion Memory system. |
| interface/api/v1/endpoints/memory.py | - | search_agent_memory | (agent_name, query, top_k, current_user) | Performs a semantic search within the vector memory of a specific agent. |
| interface/api/v1/endpoints/memory.py | - | search_global_memory | (query, top_k, current_user) | Performs a semantic search across all agent memories (if supported by the [...] |
| interface/api/v1/endpoints/system.py | - | _call_orchestrator | (action, payload) | Internal helper to send requests to the Orchestrator via ZeroMQ REQ/REP. |
| interface/api/v1/endpoints/system.py | - | get_memory_stats | (current_user) | Retrieves usage statistics for the Legion memory system via the Orchestrator. |
| interface/api/v1/endpoints/system.py | - | get_system_logs | (current_user) | Retrieves recent system logs from the Legion Orchestrator. |
| interface/api/v1/endpoints/system.py | - | get_system_metrics | (current_user) | Retrieves system performance and operational metrics from the Orchestrator. |
| interface/api/v1/endpoints/system.py | - | get_system_status | (current_user) | Retrieves the current overall system status from the Legion Orchestrator. |
| interface/api/v1/endpoints/tasks.py | - | delete_task | (task_id, current_user) | Requests the cancellation of an existing task by its UUID. |
| interface/api/v1/endpoints/tasks.py | - | post_task | (task_in, current_user) | Submits a new task to the Legion Orchestrator for processing. |
| interface/api/v1/endpoints/tasks.py | - | read_task | (task_id, current_user) | Retrieves the details and current status of a specific task by its UUID. |
| interface/api/v1/endpoints/tasks.py | - | read_tasks | (skip, limit, agent, status, current_user) | Retrieves a list of tasks from the Orchestrator, with optional filtering [...] |
| interface/api/v1/endpoints/tasks_registry.py | - | create_task | (task) | Add a task to the registry. |
| interface/api/v1/endpoints/tasks_registry.py | - | delete_task | (task_id) | Remove a task from the registry. |
| interface/api/v1/endpoints/tasks_registry.py | - | get_task | (task_id) | Retrieve a single task by ID. |
| interface/api/v1/endpoints/tasks_registry.py | - | list_tasks | (status, owner, tag) | Return tasks filtered by optional query parameters. |
| interface/api/v1/endpoints/tasks_registry.py | - | update_task | (task_id, payload) | Update fields of an existing task. |
| interface/core/security.py | - | create_access_token | (subject, expires_delta) | Creates a JWT access token. |
| interface/core/security.py | - | decode_token | (token) | Decodes a JWT token. |
| interface/core/security.py | - | get_password_hash | (password) | Hashes a plain text password using bcrypt. |
| interface/core/security.py | - | verify_password | (plain_password, hashed_password) | Verifies a plain password against a hashed password. |
| interface/crud/crud_agent.py | - | assess_agent | (agent_name) | Trigger a self-assessment for a specific agent via the Orchestrator. |
| interface/crud/crud_agent.py | - | control_agent_lifecycle | (agent_name, lifecycle_action) | Sends a lifecycle control action (start, stop, restart) to the Orchestrator. |
| interface/crud/crud_agent.py | - | create_agent | (db, agent_in) | Create a new agent. |
| interface/crud/crud_agent.py | - | delete_agent | (db, agent_id) | Delete an agent by ID. |
| interface/crud/crud_agent.py | - | dispatch_to_agent | (agent_name, message) | Dispatch a message to a specific agent via the Orchestrator. |
| interface/crud/crud_agent.py | - | get_agent | (db, agent_id) | Fetches an agent by its ID. |
| interface/crud/crud_agent.py | - | get_agent_by_name | (name) | Retrieve detailed status for a specific agent from the Orchestrator. |
| interface/crud/crud_agent.py | - | get_agent_config | (name) | Retrieve configuration for a specific agent from the Orchestrator. |
| interface/crud/crud_agent.py | - | get_agent_status | (agent_name) | Retrieve the status of a specific agent from the Orchestrator. |
| interface/crud/crud_agent.py | - | get_agents | (db, skip, limit) | Retrieve agents with pagination. |
| interface/crud/crud_agent.py | - | get_agents | () | Retrieve list of all agents and their status from the Orchestrator. |
| interface/crud/crud_agent.py | - | reload_agent_configurations | () | Sends a command to reload all agent configurations via the orchestrator. |
| interface/crud/crud_agent.py | - | update_agent | (db, db_agent, agent_in) | Update an agent. |
| interface/crud/crud_agent.py | - | update_agent_config | (agent_name, config_in) | Update the configuration of a specific agent via the Orchestrator. |
| interface/crud/crud_task.py | - | cancel_task | (task_id) | Cancel a task by ID via the Orchestrator. |
| interface/crud/crud_task.py | - | create_task | (task_in) | Create a new task by sending a request to the Orchestrator. |
| interface/crud/crud_task.py | - | get_task | (task_id) | Retrieve the status of a task by ID from the Orchestrator. |
| interface/crud/crud_task.py | - | list_tasks | (skip, limit, agent_id, status) | List tasks with optional filtering by agent_id and status. |
| interface/crud/crud_user.py | - | authenticate_user | (db, username, password) | Authenticates a user by username and password. |
| interface/crud/crud_user.py | - | create_user | (db, user) | Creates a new user in the database. |
| interface/crud/crud_user.py | - | get_user | (db, user_id) | Fetches a user by their ID. |
| interface/crud/crud_user.py | - | get_user_by_email | (db, email) | Fetches a user by their email address. |
| interface/crud/crud_user.py | - | get_user_by_username | (db, username) | Fetches a user by their username. |
| interface/crud/crud_user.py | - | get_users | (db, skip, limit) | Fetches a list of users with pagination. |
| interface/crud/crud_user.py | - | update_user | (db, db_user, user_in) | Updates an existing user. |
| interface/crud/crud_user_preference.py | - | create_user_preference | (db, user_id, preferences) | Create new user preferences (or update if they exist). |
| interface/crud/crud_user_preference.py | - | get_user_preference | (db, user_id) | Get user preferences by user ID. |
| interface/crud/crud_user_preference.py | - | update_user_preference | (db, user_id, preferences_update) | Update existing user preferences. |
| interface/db/session.py | - | get_db | () | FastAPI dependency to get a DB session. |
| interface/dependencies.py | - | _require_role | (current_user) | Needs Documentation |
| interface/dependencies.py | - | get_current_active_superuser | (current_user) | Dependency to ensure the user is an active superuser. |
| interface/dependencies.py | - | get_current_active_user | (current_user) | Dependency to get the current active user. |
| interface/dependencies.py | - | get_current_user | (db, token) | Dependency to get the current user from the JWT token. |
| interface/dependencies.py | - | get_db | () | Dependency that provides a SQLAlchemy database session. |
| interface/dependencies.py | - | require_admin_role | (user) | Needs Documentation |
| interface/dependencies.py | - | require_agent_operator_role | (user) | Needs Documentation |
| interface/dependencies.py | - | require_role | (required_role) | Dependency factory to require a specific user role. |
| interface/dependencies.py | - | require_viewer_role | (user) | Needs Documentation |
| interface/main.py | - | get_feed | () | Returns the latest events from the orchestrator as JSON. |
| interface/main.py | - | on_startup | () | Needs Documentation |
| interface/main.py | - | push_updates | () | Example background task to simulate pushing feed updates. |
| interface/main.py | - | read_root | (request) | Renders the main feed HTML page. |
| interface/main.py | - | root | () | Needs Documentation |
| interface/main.py | - | send_to_all | (message) | Sends a message to all connected WebSocket clients. |
| interface/main.py | - | websocket_endpoint | (websocket) | Sends orchestrator events to the client via websocket. |
| interface/main.py | - | websocket_feed | (websocket) | WebSocket endpoint for the live feed. |
| interface/main.py | SecurityHeadersMiddleware | dispatch | (self, request, call_next) | Needs Documentation |
| interface/migrations/env.py | - | ensure_db_directory_exists | () | Needs Documentation |
| interface/migrations/env.py | - | run_migrations_offline | () | Run migrations in 'offline' mode. |
| interface/migrations/env.py | - | run_migrations_online | () | Run migrations in 'online' mode. |
| interface/migrations/initial_migration.py | - | downgrade | () | Needs Documentation |
| interface/migrations/initial_migration.py | - | upgrade | () | Needs Documentation |
| interface/migrations/versions/0c41691da765_add_agents_table.py | - | downgrade | () | Downgrade schema. |
| interface/migrations/versions/0c41691da765_add_agents_table.py | - | upgrade | () | Upgrade schema. |
| interface/migrations/versions/c8ebbab9d988_update_user_model_with_role_last_login_.py | - | downgrade | () | Downgrade schema. |
| interface/migrations/versions/c8ebbab9d988_update_user_model_with_role_last_login_.py | - | upgrade | () | Upgrade schema. |
| interface/migrations/versions/initial_users_table.py | - | downgrade | () | Needs Documentation |
| interface/migrations/versions/initial_users_table.py | - | upgrade | () | Needs Documentation |
| interface/orchestrator_comm.py | - | send_request | (command, timeout_ms) | Sends a command to the orchestrator via ZeroMQ and awaits the response. |
| interface/websocket_manager.py | ConnectionManager | __init__ | (self) | Needs Documentation |
| interface/websocket_manager.py | ConnectionManager | broadcast | (self, message) | Broadcasts a message to all active connections. |
| interface/websocket_manager.py | ConnectionManager | connect | (self, websocket) | Needs Documentation |
| interface/websocket_manager.py | ConnectionManager | disconnect | (self, websocket) | Needs Documentation |
| interface/websocket_manager.py | ConnectionManager | send_personal_message | (self, message, websocket) | Sends a message to a specific WebSocket client. |
| legion/agents/base.py | BaseAgent | __init__ | (self, name, config, llm_client, state_manager) | Initialize the Base Agent with dependency injection for LLM client and [...] |
| legion/agents/base.py | BaseAgent | call_llm | (self, thread_id, history, **override_kwargs) | Centralized LLM invocation: selects dynamic rules and calls the LLM client. |
| legion/agents/base.py | BaseAgent | fetch_thread_history | (self, channel_id, thread_id, limit) | Fetch the last N messages from a Discord channel thread. |
| legion/agents/base.py | BaseAgent | get_message_embedding | (self, text) | Generate an embedding for the given text, safely handling errors. |
| legion/agents/base.py | BaseAgent | handle_message | (self, content, author, timestamp, context) | Handle a message, manage memory, and interact with LLM and Discord. |
| legion/agents/base.py | BaseAgent | loop | () | Needs Documentation |
| legion/agents/base.py | BaseAgent | make_hashable_text | (text) | Needs Documentation |
| legion/agents/base.py | BaseAgent | mem_retrieve | (self, embedding, top_k, tags, timestamp, base_dir) | Helper to retrieve vector memories with optional tags and timestamp. |
| legion/agents/base.py | BaseAgent | mem_store | (self, snippets, tags, timestamp, base_dir) | Helper to store vector memories with optional tags, timestamp; [...] |
| legion/agents/base.py | BaseAgent | post_to_discord | (self, message) | Post a message to the agent's Discord channel, splitting if too long. |
| legion/agents/base.py | BaseAgent | self_assess | (self) | Run a self-assessment and post the result to Discord. |
| legion/agents/base.py | BaseAgent | start_self_assessment | (self, interval_seconds) | Start the self-assessment loop if not already running. |
| legion/agents/base.py | BaseAgent | stop_self_assessment | (self) | Needs Documentation |
| legion/agents/base.py | BaseAgent | store_message | (self, payload, message_id, metadata) | Store a message in the agent's memory. |
| legion/agents/contracts.py | - | validate_all_agents | (instances) | Validate that each agent instance implements its contract methods. |
| legion/agents/contracts.py | IArchitectAgent | compose_summary | (self) | Needs Documentation |
| legion/agents/contracts.py | IArchitectAgent | extract_llm_metrics | (self) | Needs Documentation |
| legion/agents/contracts.py | IArchitectAgent | handle_review | (self) | Needs Documentation |
| legion/agents/contracts.py | IArchitectAgent | list_repo | (self) | Needs Documentation |
| legion/agents/contracts.py | IArchitectAgent | read_logs | (self) | Needs Documentation |
| legion/agents/contracts.py | IArchitectAgent | set_log_paths | (self, log_path, report_path) | Needs Documentation |
| legion/agents/contracts.py | IEchoAgent | handle_echo | (self, message) | Needs Documentation |
| legion/agents/contracts.py | IHealthcheckAgent | handle_healthcheck | (self) | Needs Documentation |
| legion/agents/contracts.py | IMetricsAgent | compose_summary | (self) | Needs Documentation |
| legion/agents/contracts.py | IMetricsAgent | get_agent_channels | (self) | Needs Documentation |
| legion/agents/contracts.py | IMetricsAgent | handle_report | (self) | Needs Documentation |
| legion/agents/contracts.py | IMetricsAgent | read_logs | (self) | Needs Documentation |
| legion/agents/contracts.py | IMetricsAgent | report | (self) | Needs Documentation |
| legion/agents/contracts.py | IMetricsAgent | set_log_paths | (self, log_path) | Needs Documentation |
| legion/agents/contracts.py | ITherapistAgent | compose_summary | (self) | Needs Documentation |
| legion/agents/contracts.py | ITherapistAgent | handle_self_assessment | (self) | Needs Documentation |
| legion/agents/contracts.py | ITherapistAgent | read_logs | (self) | Needs Documentation |
| legion/agents/contracts.py | ITherapistAgent | set_log_paths | (self, log_path) | Needs Documentation |
| legion/agents/memory.py | LegionAgentMemory | __init__ | (self, agent_name, memory_dir) | Initialize agent memory. |
| legion/agents/memory.py | LegionAgentMemory | _load_memory | (self) | Load memory from file. |
| legion/agents/memory.py | LegionAgentMemory | _save_memory | (self) | Save memory to file. |
| legion/agents/memory.py | LegionAgentMemory | clear | (self) | Clear all memory. |
| legion/agents/memory.py | LegionAgentMemory | delete | (self, key) | Delete a value from memory. |
| legion/agents/memory.py | LegionAgentMemory | get | (self, key, default) | Get a value from memory. |
| legion/agents/memory.py | LegionAgentMemory | get_all | (self) | Get all memory. |
| legion/agents/memory.py | LegionAgentMemory | get_task_log | (self) | Get task log. |
| legion/agents/memory.py | LegionAgentMemory | log_task | (self, task) | Log a task to memory. |
| legion/agents/memory.py | LegionAgentMemory | set | (self, key, value) | Set a value in memory. |
| legion/agents/python/architect.py | ArchitectAgent | __init__ | (self, name, config, orchestrator_ref, llm_client) | Needs Documentation |
| legion/agents/python/architect.py | ArchitectAgent | compose_summary | (self) | Compose summary of recent task logs and LLM metrics. |
| legion/agents/python/architect.py | ArchitectAgent | extract_llm_metrics | (self) | Extract LLM-related metrics from report file. |
| legion/agents/python/architect.py | ArchitectAgent | handle_review | (self, pr_diff) | Review code changes and provide feedback. |
| legion/agents/python/architect.py | ArchitectAgent | list_files | (startpath) | Needs Documentation |
| legion/agents/python/architect.py | ArchitectAgent | list_repo | (self) | Get list of files/dirs in repo. |
| legion/agents/python/architect.py | ArchitectAgent | read_logs | (self) | Read JSONL task log entries. |
| legion/agents/python/architect.py | ArchitectAgent | retrieve_feedback | (self, query, k) | Retrieve relevant feedback memories based on embeddings. |
| legion/agents/python/architect.py | ArchitectAgent | set_log_paths | (self, log_path, report_path) | Set paths to task log and report log for reading logs and metrics. |
| legion/agents/python/echo.py | EchoAgent | __init__ | (self, orchestrator) | Needs Documentation |
| legion/agents/python/echo.py | EchoAgent | handle_echo | (self, message) | Needs Documentation |
| legion/agents/python/healthcheck.py | HealthcheckAgent | __init__ | (self, orchestrator, llm_client) | Needs Documentation |
| legion/agents/python/healthcheck.py | HealthcheckAgent | check_dependencies | (self) | Check status of system dependencies. |
| legion/agents/python/healthcheck.py | HealthcheckAgent | generate_report | (self) | Generate comprehensive health report. |
| legion/agents/python/healthcheck.py | HealthcheckAgent | get_status | (self) | Get current system status. |
| legion/agents/python/healthcheck.py | HealthcheckAgent | handle_healthcheck | (self) | Needs Documentation |
| legion/agents/python/healthcheck.py | HealthcheckAgent | health_loop | (self) | Main health monitoring loop. |
| legion/agents/python/healthcheck.py | HealthcheckAgent | start | (self) | Start the health monitoring loop. |
| legion/agents/python/healthcheck.py | HealthcheckAgent | stop | (self) | Stop the health monitoring loop. |
| legion/agents/python/metrics.py | MetricsAgent | __init__ | (self, name, config, orchestrator_ref, llm_client) | Initialize the MetricsAgent with name, config, orchestrator reference, and [...] |
| legion/agents/python/metrics.py | MetricsAgent | _default_prompt | (self) | Return the default system prompt for the MetricsAgent. |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | analyze_metrics | (self) | Stub method to analyze collected metrics and generate insights. |
| legion/agents/python/metrics.py | MetricsAgent | collect_metrics | (self) | Stub method to collect system metrics. |
| legion/agents/python/metrics.py | MetricsAgent | compose_summary | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | get_agent_channels | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | handle_report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | read_logs | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | report | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | report_metrics | (self) | Stub method to report metrics and insights to relevant channels or logs. |
| legion/agents/python/metrics.py | MetricsAgent | retrieve_feedback | (self) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | retrieve_memories | (self, embeddings) | Needs Documentation |
| legion/agents/python/metrics.py | MetricsAgent | set_log_paths | (self, log_path) | Needs Documentation |
| legion/agents/python/ping.py | PingAgent | __init__ | (self, orchestrator) | Needs Documentation |
| legion/agents/python/ping.py | PingAgent | handle_ping | (self) | Needs Documentation |
| legion/agents/python/therapist.py | TherapistAgent | __init__ | (self, name, config, orchestrator_ref, llm_client) | Initialize the TherapistAgent with name, config, orchestrator reference, [...] |
| legion/agents/python/therapist.py | TherapistAgent | compose_summary | (self) | Needs Documentation |
| legion/agents/python/therapist.py | TherapistAgent | fallback_response | (self, reason) | Generate a safe fallback message for invalid or out-of-scope requests. |
| legion/agents/python/therapist.py | TherapistAgent | handle_self_assessment | (self, content, context) | Needs Documentation |
| legion/agents/python/therapist.py | TherapistAgent | read_logs | (self) | Needs Documentation |
| legion/agents/python/therapist.py | TherapistAgent | retrieve_memories | (self, embeddings) | Needs Documentation |
| legion/agents/python/therapist.py | TherapistAgent | set_log_paths | (self, log_path) | Needs Documentation |
| legion/agents/python/therapist.py | TherapistAgent | validate_request | (self, content, context) | Validate incoming request against core directives: |
| legion/agents/python/ux_designer.py | UxDesignerAgent | __init__ | (self, name, config, orchestrator_ref, llm_client) | Needs Documentation |
| legion/agents/python/ux_designer.py | UxDesignerAgent | handle_critique | (self) | Needs Documentation |
| legion/agents/therapist/validation.py | - | aligns_with_strategic_directives | (directive_to_check) | Needs Documentation |
| legion/agents/therapist/validation.py | - | logical_flow_is_valid | (directive_to_check) | Needs Documentation |
| legion/agents/therapist/validation.py | - | therapist_validate | (request) | Needs Documentation |
| legion/cli.py | - | main | () | Needs Documentation |
| legion/core/db/migrations/0001_initial.py | - | downgrade | () | Needs Documentation |
| legion/core/db/migrations/0001_initial.py | - | upgrade | () | Needs Documentation |
| legion/core/db/migrations/0002_create_tasks.py | - | downgrade | (migrator) | Drop tasks table. |
| legion/core/db/migrations/0002_create_tasks.py | - | upgrade | (migrator) | Create tasks table. |
| legion/core/db/models.py | Agent | __repr__ | (self) | Needs Documentation |
| legion/core/db/models.py | Agent | get_active_task | (self) | Get the currently active task for this agent, if any. |
| legion/core/db/models.py | Agent | get_pending_tasks | (self) | Get all pending tasks for this agent. |
| legion/core/db/models.py | Agent | to_dict | (self) | Convert agent to dictionary representation. |
| legion/core/db/models.py | Agent | update_status | (self, status) | Update agent status and last heartbeat. |
| legion/core/db/models.py | Task | __repr__ | (self) | Needs Documentation |
| legion/core/db/models.py | Task | cancel | (self) | Mark task as cancelled. |
| legion/core/db/models.py | Task | complete | (self, result) | Mark task as completed with optional result. |
| legion/core/db/models.py | Task | fail | (self, error) | Mark task as failed with error message. |
| legion/core/db/models.py | Task | start | (self) | Mark task as started. |
| legion/core/db/models.py | Task | to_dict | (self) | Convert task to dictionary representation. |
| legion/core/db_utils.py | - | init_db | (db_path) | Initialize the database schema (stub). |
| legion/core/db_utils.py | - | run_migrations | (db_path) | Run database migrations (stub). |
| legion/core/di_container.py | - | get_llm_client | () | Get the registered LLM client. |
| legion/core/di_container.py | - | get_memory_manager | () | Get the registered memory manager. |
| legion/core/di_container.py | - | get_state_manager | () | Get the registered state manager. |
| legion/core/di_container.py | DIContainer | __init__ | (self) | Needs Documentation |
| legion/core/di_container.py | DIContainer | clear | (self) | Clear all registered instances and factories (useful for tests). |
| legion/core/di_container.py | DIContainer | get | (self, service_type) | Retrieve a service instance by its type. |
| legion/core/di_container.py | DIContainer | register_factory | (self, service_type, factory) | Register a factory function for creating a service instance. |
| legion/core/di_container.py | DIContainer | register_instance | (self, service_type, instance) | Register a pre-created instance of a service. |
| legion/core/indexing.py | - | placeholder_indexing | (docs, field) | Build a simple inverted index for a list of docs. |
| legion/core/init_memory.py | - | main | () | Needs Documentation |
| legion/core/interfaces.py | ILLMClient | call | (self, messages, **kwargs) | Call the LLM with a list of messages and return the response. |
| legion/core/interfaces.py | ILLMClient | get_embedding | (self, text) | Generate an embedding for the given text. |
| legion/core/interfaces.py | IMemoryManager | log_task | (self, task) | Log a task or event to memory. |
| legion/core/interfaces.py | IMemoryManager | retrieve_memories | (self, agent_name, embedding, top_k, category) | Retrieve memories based on embedding similarity. |
| legion/core/interfaces.py | IMemoryManager | store_memories | (self, agent_name, snippets, base_dir) | Store multiple memory snippets with embeddings. |
| legion/core/interfaces.py | IMemoryManager | store_memory | (self, id, content, metadata) | Store a memory entry with optional metadata. |
| legion/core/interfaces.py | IStateManager | get_state | (self, key) | Retrieve a state value by key. |
| legion/core/interfaces.py | IStateManager | log_task | (self, task) | Log a task or event to persistent state. |
| legion/core/interfaces.py | IStateManager | set_state | (self, key, value) | Set a state value by key. |
| legion/core/llm_client.py | LLMClient | __init__ | (self, api_key, model, api_base, **default_kwargs) | Initialize the LLM client with optional API key, model, base URL, and [...] |
| legion/core/llm_client.py | LLMClient | generate | (self, agent_name, thread_id, dynamic_rules, history, **override_kwargs) | Generate a completion using dynamic rules and history. |
| legion/core/logging_config.py | - | setup_logging | (log_level) | Configure structured JSON logging for the Legion system. |
| legion/core/logging_config.py | JsonFormatter | format | (self, record) | Needs Documentation |
| legion/core/network.py | - | health_check | (url, timeout) | HTTP GET, return True if 200 else False. |
| legion/core/network.py | - | placeholder_network | (url, timeout) | Perform a basic HTTP GET health check and return status and response time. |
| legion/core/prompt_builder.py | PromptBuilder | build | (system_prompt, memories, thread_history, user_query, memory_prefix, reflection_prompt) | Constructs a list of message dicts for LLM consumption. |
| legion/core/state.py | StateManager | __init__ | (self, state_dir) | Initialize state directory, files, and default config. |
| legion/core/state.py | StateManager | _save_state | (self, state) | Save state to JSON file. |
| legion/core/state.py | StateManager | add_feedback | (self, feedback) | Add feedback entry. |
| legion/core/state.py | StateManager | adjust_confidence_threshold | (self, new_threshold) | Adjust confidence threshold in config. |
| legion/core/state.py | StateManager | get_recent_errors | (self, limit) | Get recent errors from log. |
| legion/core/state.py | StateManager | get_recent_tasks | (self, limit) | Get recent tasks from log. |
| legion/core/state.py | StateManager | get_state | (self) | Get current state. |
| legion/core/state.py | StateManager | log_error | (self, error) | Append error to error log. |
| legion/core/state.py | StateManager | log_task | (self, task) | Append task to task log. |
| legion/core/state.py | StateManager | log_telemetry | (self, event) | Append a telemetry event to the task log (or a dedicated telemetry log if [...] |
| legion/core/state.py | StateManager | update_state | (self, updates) | Update state with new values. |
| legion/core/utils/chroma_client.py | ChromaClient | __init__ | (self, persist_directory, embedding_model) | Initializes the Chroma client and collection. |
| legion/core/utils/chroma_client.py | ChromaClient | add_embedding | (self, embedding_id, embedding, metadata) | Alias for store_embedding to add or update an embedding. |
| legion/core/utils/chroma_client.py | ChromaClient | compute_similarity | (self, emb1, emb2) | Compute cosine similarity between two embeddings. |
| legion/core/utils/chroma_client.py | ChromaClient | create_embedding | (self, text) | Generate an embedding for the given text via OpenAI. |
| legion/core/utils/chroma_client.py | ChromaClient | query_embeddings | (self, embedding, top_k) | Alias for retrieve_similar_embeddings with no threshold filtering. |
| legion/core/utils/chroma_client.py | ChromaClient | retrieve_similar_embeddings | (self, query_embedding, top_k, threshold) | Retrieve embeddings with similarity >= threshold. |
| legion/core/utils/chroma_client.py | ChromaClient | store_embedding | (self, embedding_id, embedding, metadata) | Add or update an embedding in the Chroma collection. |
| legion/core/utils/chroma_client.py | ChromaClient | validate_embedding | (self, embedding, threshold) | Validate if any stored embedding meets or exceeds the similarity threshold. |
| legion/core/utils/indexing.py | - | extract_keywords | (text) | Extracts keywords from text (stub). |
| legion/core/utils/indexing.py | - | index_text | (text) | Placeholder for text indexing logic. |
| legion/core/utils/indexing.py | - | render_feed_item | (agent_name, message, fields) | Placeholder for rendering a feed item (e.g., Discord embed). |
| legion/core/utils/network.py | - | fetch_with_retries | (url, retries, delay) | Fetch URL with basic retry logic. |
| legion/database/chroma_interface.py | - | query_context | (query_text) | Queries ChromaDB for context related to the query_text. |
| legion/discord/commands.py | - | _safe_send | (channel, *args, **kwargs) | Send a message only if the channel supports .send() |
| legion/discord/commands.py | - | setup | (bot) | Needs Documentation |
| legion/discord/commands.py | LegionCommandCog | __init__ | (self, bot, orchestrator) | Needs Documentation |
| legion/discord/commands.py | LegionCommandCog | _alert_subscribe_impl | (self, ctx) | Needs Documentation |
| legion/discord/commands.py | LegionCommandCog | _config_agent_impl | (self, ctx, agent_name, model, temperature, max_tokens) | Business logic for config_agent command. |
| legion/discord/commands.py | LegionCommandCog | _feedback_impl | (self, ctx, message_id, rating) | Needs Documentation |
| legion/discord/commands.py | LegionCommandCog | _log_to_agent_logs | (self, message) | Helper to post a log message to #agent-logs. |
| legion/discord/commands.py | LegionCommandCog | _state_query_impl | (self, ctx, key) | Needs Documentation |
| legion/discord/commands.py | LegionCommandCog | alert_subscribe | (self, ctx) | /alert subscribe |
| legion/discord/commands.py | LegionCommandCog | config_agent | (self, ctx, agent_name, model, temperature, max_tokens) | /config agent agent_name model temperature max_tokens |
| legion/discord/commands.py | LegionCommandCog | feedback | (self, ctx, message_id, rating) | /feedback message_id rating |
| legion/discord/commands.py | LegionCommandCog | send_alert_to_subscribers | (self, alert_message) | Send an alert DM to all subscribed users. |
| legion/discord/commands.py | LegionCommandCog | state_query | (self, ctx, key) | /state query key |
| legion/middleware/__init__.py | - | run_middleware_pipeline | (request_payload, confidence_threshold) | Runs the full middleware validation pipeline: |
| legion/middleware/hallucination_guard.py | - | guard_response | (response, threshold) | Checks the confidence score of a response and flags potential hallucinations. |
| legion/middleware/tests/test_middleware.py | TestMiddleware | test_chroma_query | (self) | Needs Documentation |
| legion/middleware/tests/test_middleware.py | TestMiddleware | test_hallucination_guard | (self) | Needs Documentation |
| legion/middleware/tests/test_middleware.py | TestMiddleware | test_middleware_pipeline | (self) | Needs Documentation |
| legion/middleware/tests/test_middleware.py | TestMiddleware | test_validate_directive | (self) | Needs Documentation |
| legion/middleware/validator.py | - | _load_directives_config | () | Loads the directives configuration from the YAML file. |
| legion/middleware/validator.py | - | validate_directive | (payload) | Validates an agent directive payload. |
| legion/orchestrator.py | Orchestrator | __init__ | (self, post_agent_message, pid_file, state_manager, llm_client) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | _acquire_lock | (self) | Acquire an exclusive lock on the PID file. |
| legion/orchestrator.py | Orchestrator | _get_channel_id | (self, agent_name) | Return the Discord channel ID for a given agent name, or the general [...] |
| legion/orchestrator.py | Orchestrator | _release_lock | (self) | Release the lock and clean up the PID file. |
| legion/orchestrator.py | Orchestrator | _release_lock_atexit | (self) | Synchronous lock release wrapper for atexit. |
| legion/orchestrator.py | Orchestrator | _setup_signal_handlers | (self) | Set up signal handlers for graceful shutdown. |
| legion/orchestrator.py | Orchestrator | _zmq_pub_loop | (self) | Handles periodic ZMQ PUB broadcasts (e.g., heartbeats, task updates). |
| legion/orchestrator.py | Orchestrator | _zmq_rep_loop | (self) | Handles incoming ZMQ REP requests. |
| legion/orchestrator.py | Orchestrator | add_alert_subscriber | (self, user_id) | Add a user to the alert subscription list. |
| legion/orchestrator.py | Orchestrator | agent_comm_router | (self, msg) | Central router deciding which agent receives a message. |
| legion/orchestrator.py | Orchestrator | agent_registry | (self) | Returns agent configuration registry. |
| legion/orchestrator.py | Orchestrator | ask | (self, agent_name, prompt, context) | Sends a prompt to a specific agent and returns its response. |
| legion/orchestrator.py | Orchestrator | assess_all_agents | (self) | Triggers self-assessment for all agents. |
| legion/orchestrator.py | Orchestrator | broadcast | (self, prompt) | Sends a prompt to all registered agents. |
| legion/orchestrator.py | Orchestrator | call_directive | (self, directive_name, **kwargs) | Invoke a registered directive on an agent. |
| legion/orchestrator.py | Orchestrator | comment_on_post | (self, agent_name, target_agent, comment) | Logs a comment on another agent's post. |
| legion/orchestrator.py | Orchestrator | create_new_task | (self, payload) | Validates a task payload using the middleware pipeline and then, if valid, |
| legion/orchestrator.py | Orchestrator | deliver_message | (self, to_agent, payload) | Delivers a message to an agent object and logs it. |
| legion/orchestrator.py | Orchestrator | dispatch | (self, agent_key, payload) | Dispatches a task to the specified agent. |
| legion/orchestrator.py | Orchestrator | dispatch_command | (self, command) | Dispatch incoming command based on 'action' field and return response. |
| legion/orchestrator.py | Orchestrator | dispatch_message | (self, agent_name, content, author, timestamp) | Dispatches a message to an agent, processes it, and returns a response. |
| legion/orchestrator.py | Orchestrator | get_agent_channel | (self, agent_name) | Returns Discord channel ID for an agent. |
| legion/orchestrator.py | Orchestrator | get_agent_config_info | (self, agent_name) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_agent_list | (self) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_agent_status | (self, agent_name) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_alert_subscribers | (self) | Return the set of alert subscriber user IDs. |
| legion/orchestrator.py | Orchestrator | get_dummy_logs | (self) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_memory_system_stats | (self) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_state_key | (self, key) | Return the value for a given key from the central state. |
| legion/orchestrator.py | Orchestrator | get_system_metrics | (self) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_system_status | (self) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_task_details | (self, task_id) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | get_task_list | (self, filters) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | handle_signal | (signum, frame) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | init_context | (self, namespace, **kwargs) | Returns a context dict for agent interactions. |
| legion/orchestrator.py | Orchestrator | init_zmq_pub_server | (self, bind_address) | Initializes the ZeroMQ PUB server. |
| legion/orchestrator.py | Orchestrator | init_zmq_rep_server | (self, bind_address) | Initializes the ZeroMQ REP server. |
| legion/orchestrator.py | Orchestrator | load_agent | (self, key) | Load or return a cached agent instance by its key. |
| legion/orchestrator.py | Orchestrator | load_agent_configs | (self) | Load agent configurations from YAML files in the `legion/configs` directory. |
| legion/orchestrator.py | Orchestrator | load_yaml | (self, path) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | notify_agent | (self, agent_name, message) | Logs a notification for an agent. |
| legion/orchestrator.py | Orchestrator | periodic_assessments | (self, interval_minutes) | Periodically triggers self-assessment for all agents. |
| legion/orchestrator.py | Orchestrator | post_update | (self, agent_name, content, files) | Logs an update for an agent. |
| legion/orchestrator.py | Orchestrator | react_to_post | (self, agent_name, target_agent, emoji) | Logs a reaction to another agent's post. |
| legion/orchestrator.py | Orchestrator | receive_from_therapist | (self, message) | Handle Therapist → Orchestrator callbacks. |
| legion/orchestrator.py | Orchestrator | register_test_agents | (self) | Register dummy agents for testing. |
| legion/orchestrator.py | Orchestrator | reload_agent_configs | (self, llm_client) | Reloads agent configurations from YAML files and updates all agents. |
| legion/orchestrator.py | Orchestrator | request_assistance | (self, agent_name, issue) | Logs a request for assistance. |
| legion/orchestrator.py | Orchestrator | request_task_cancellation | (self, task_id) | Needs Documentation |
| legion/orchestrator.py | Orchestrator | restart_agent | (self, agent_name) | Placeholder: Restart the specified agent. |
| legion/orchestrator.py | Orchestrator | run | (self, interval) | Main orchestrator loop. Now relies on ZMQ REP server for commands. |
| legion/orchestrator.py | Orchestrator | run_once | (self, event) | Simulates a single orchestrator event loop iteration. |
| legion/orchestrator.py | Orchestrator | run_self_assess_all | (self) | Run self_assess() on all agents, logging exceptions. |
| legion/orchestrator.py | Orchestrator | self_assess | (self, agent_name) | Triggers self-assessment for an agent using recent logs. |
| legion/orchestrator.py | Orchestrator | send_message | (self, from_agent, to_agent, payload) | Sends a message from one agent to another and logs it. |
| legion/orchestrator.py | Orchestrator | send_to_therapist | (self, task_id, payload) | Queue a message for the Therapist agent. |
| legion/orchestrator.py | Orchestrator | shutdown | (self, signal_name) | Gracefully shuts down the orchestrator. |
| legion/orchestrator.py | Orchestrator | start_agent | (self, agent_name) | Placeholder: Start the specified agent. |
| legion/orchestrator.py | Orchestrator | stop_agent | (self, agent_name) | Placeholder: Stop the specified agent. |
| legion/orchestrator.py | Orchestrator | stop_zmq_servers | (self) | Stop the ZMQ REP and PUB servers and cancel related tasks. |
| legion/orchestrator.py | Orchestrator | submit_feedback | (self, feedback) | Submit user or audit feedback into the central state store. |
| legion/orchestrator.py | Orchestrator | update_agent_config | (self, agent_name, model, temperature, max_tokens) | Update the config for a given agent and reload its attributes. |
| legion/orchestrator/capability_indexer.py | - | get_capabilities | () | Return mapping of agent names to capability method names. |
| legion/orchestrator/routing_map.py | - | get_agents_for | (capability) | Return a list of agents that support the given capability. |
| legion/orchestrator/routing_map.py | - | get_all_capabilities | () | Get the full capability routing table. |
| legion/orchestrator/routing_map.py | - | rebuild_routing_map | (agent_statuses) | Build the routing map from agent status information. |
| legion/orchestrator/state_repository.py | - | _default_registry | () | Needs Documentation |
| legion/orchestrator/state_repository.py | - | add_task | (task_id, tags, owner, agent) | Register a new task with default status PENDING. |
| legion/orchestrator/state_repository.py | - | get_task | (task_id) | Retrieve a task record by ID. |
| legion/orchestrator/state_repository.py | - | list_tasks | () | List tasks matching optional filters. |
| legion/orchestrator/state_repository.py | - | remove_task | (task_id) | Delete a task from the registry. |
| legion/orchestrator/state_repository.py | - | update_task | (task_id) | Update fields on an existing task record. |
| legion/orchestrator/state_repository.py | - | update_task_status | (task_id, status) | Update the status of a tracked task. |
| legion/orchestrator/tag_middleware.py | - | decorator | (func) | Needs Documentation |
| legion/orchestrator/tag_middleware.py | - | tag_payload | (tags) | Decorator to attach tags to a payload before calling the wrapped function. |
| legion/orchestrator/tag_middleware.py | - | wrapper | (payload, *args, **kwargs) | Needs Documentation |
| legion/ports.py | - | get_chroma_url | (default_host) | Constructs the Chroma API URL using the configured port. |
| legion/ports.py | - | get_port | (service_key) | Retrieves the allocated port for a given service key. |
| legion/ports.py | - | load_runtime_ports | (env_file_path) | Loads port configurations from the specified .env file. |
| legion/utils/logging.py | - | _test_logging | (log_level) | Test function to demonstrate logging at various levels. |
| legion/utils/logging.py | - | log_uncaught_exception | (exc_type, exc_value, exc_traceback) | Needs Documentation |
| legion/utils/logging.py | - | setup_legion_logging | (log_level_str, log_to_console, log_file_path) | Configures structured JSON logging for the Legion application. |
| legion/utils/logging.py | JsonFormatter | format | (self, record) | Needs Documentation |
| legion/utils/port_conflict_checker.py | - | check_ports_available | (port_map, environment) | Checks if ports are available and within the allowed range. |
| legion/utils/port_conflict_checker.py | - | validate_port_range | (port, environment) | Validates that a port falls within the allowed range for the environment. |
| memory/legion_memory.py | - | retrieve_memories | (agent_name, embedding, top_k, base_dir) | Needs Documentation |
| memory/legion_memory.py | - | store_memories | (agent_name, snippets, base_dir) | Needs Documentation |
| memory/legion_memory.py | LegionAgentMemory | __init__ | (self, agent_name, base_dir) | Initialize memory for a specific agent. |
| memory/legion_memory.py | LegionAgentMemory | _cosine_similarity | (vec1, vec2) | Compute cosine similarity between two vectors. |
| memory/legion_memory.py | LegionAgentMemory | _ensure_db | (self) | Ensures the SQLite DB and task_log table exist. |
| memory/legion_memory.py | LegionAgentMemory | _load_data | (self) | Loads agent memory data from disk. |
| memory/legion_memory.py | LegionAgentMemory | _vector_store_path | (agent_name, base_dir) | Returns the path to the agent's vector store JSONL file. |
| memory/legion_memory.py | LegionAgentMemory | _write | () | Needs Documentation |
| memory/legion_memory.py | LegionAgentMemory | add_raw_memory | (self, text, metadata) | Adds raw text to the memory, potentially for later processing. |
| memory/legion_memory.py | LegionAgentMemory | get | (self, key) | Gets a value from memory. |
| memory/legion_memory.py | LegionAgentMemory | get_document | (self, name, version) | Retrieves a document (optionally by version). |
| memory/legion_memory.py | LegionAgentMemory | get_task_log | (self) | Retrieves the agent's task log from the DB. |
| memory/legion_memory.py | LegionAgentMemory | list_documents | (self) | Lists all documents for the agent. |
| memory/legion_memory.py | LegionAgentMemory | list_versions | (self, name) | Lists all versions of a document. |
| memory/legion_memory.py | LegionAgentMemory | log_task | (self, task) | Logs a task to the SQLite DB. |
| memory/legion_memory.py | LegionAgentMemory | retrieve_memories | (cls, agent_name, embedding, top_k, base_dir) | Loads or creates the vector index for that agent. Returns up to topK text [...] |
| memory/legion_memory.py | LegionAgentMemory | save | (self) | Saves memory data to disk. |
| memory/legion_memory.py | LegionAgentMemory | save_document | (self, name, content) | Saves a versioned document for the agent. |
| memory/legion_memory.py | LegionAgentMemory | set | (self, key, value) | Sets a value in memory and saves. |
| memory/legion_memory.py | LegionAgentMemory | store_memories | (cls, agent_name, snippets, base_dir) | Upserts the given snippets into the agent's vector store. Retries once on [...] |
| metrics/exporter.py | - | start_metrics_server | (port) | Start Prometheus metrics HTTP server on the specified port. |
| middleware/src/main.py | - | attach_context | (request, call_next) | Needs Documentation |
| middleware/src/main.py | - | get_context | (agent_name, interaction_id) | Needs Documentation |
| middleware/src/main.py | - | health | () | Needs Documentation |
| middleware/src/main.py | - | invoke | (req) | Needs Documentation |
| middleware/src/main.py | - | metrics | () | Needs Documentation |
| middleware/src/main.py | - | orchestrate | (payload) | Needs Documentation |
| middleware/src/main.py | - | verify_token | (request) | Needs Documentation |
| middleware/src/middleware/context_manager.py | ContextManager | __init__ | (self, orchestrator_client) | Needs Documentation |
| middleware/src/middleware/context_manager.py | ContextManager | attach_core_directives | (self, context) | Needs Documentation |
| middleware/src/middleware/context_manager.py | ContextManager | log_interaction | (self, interaction) | Needs Documentation |
| middleware/src/middleware/context_manager.py | ContextManager | route | (self, payload) | Needs Documentation |
| middleware/src/middleware/directive_compliance.py | DirectiveCompliance | __init__ | (self) | Needs Documentation |
| middleware/src/middleware/directive_compliance.py | DirectiveCompliance | check | (self, request_text, request_metadata, agent_id) | Checks the request against predefined agent directives. |
| middleware/src/middleware/hallucination_guard.py | HallucinationGuard | __init__ | (self, threshold) | Needs Documentation |
| middleware/src/middleware/hallucination_guard.py | HallucinationGuard | filter | (self, response) | Add warning if confidence < threshold |
| middleware/src/middleware/middleware.py | RequestMiddleware | __init__ | (self, chroma_client, directive_checker) | Needs Documentation |
| middleware/src/middleware/middleware.py | RequestMiddleware | process_request | (self, request_text, request_metadata) | Processes an incoming request, performs embedding validation and directive [...] |
| middleware/tests/test_main.py | - | client | () | Needs Documentation |
| middleware/tests/test_main.py | - | test_context_endpoint | (client, monkeypatch) | Needs Documentation |
| middleware/tests/test_main.py | - | test_health | (client) | Needs Documentation |
| middleware/tests/test_main.py | - | test_metrics | (client) | Needs Documentation |
| middleware/tests/test_main.py | DummyColl | get | (self, ids) | Needs Documentation |
| middleware/tests/test_middleware_chroma_client.py | - | dummy_delete | (ids) | Needs Documentation |
| middleware/tests/test_middleware_chroma_client.py | - | dummy_get_or_create_collection | (name) | Needs Documentation |
| middleware/tests/test_middleware_chroma_client.py | - | dummy_query | (query_embeddings, n_results) | Needs Documentation |
| middleware/tests/test_middleware_chroma_client.py | - | test_upsert_and_query | (monkeypatch) | Needs Documentation |
| middleware/tests/test_middleware_chroma_client.py | Coll | upsert | (self, docs) | Needs Documentation |
| scripts/agent_instantiation_guard.py | - | class_name_to_agent_key | (class_name) | Converts Agent ClassName to snake_case_key (e.g., ArchitectAgent -> architect). |
| scripts/agent_instantiation_guard.py | - | main | () | Needs Documentation |
| scripts/agent_instantiation_guard.py | AgentInstantiationCodemod | __init__ | (self, context) | Needs Documentation |
| scripts/agent_instantiation_guard.py | AgentInstantiationCodemod | add_args | (parser) | Needs Documentation |
| scripts/agent_instantiation_guard.py | AgentInstantiationCodemod | leave_Call | (self, original_node, updated_node) | Needs Documentation |
| scripts/agent_instantiation_guard.py | AgentInstantiationCodemod | should_skip_file | (self) | Checks if the current file is legion/orchestrator.py. |
| scripts/agent_instantiation_guard.py | AgentInstantiationCodemod | transform_module_impl | (self, tree) | Needs Documentation |
| scripts/agent_instantiation_guard.py | AgentInstantiationCodemod | visit_Call | (self, node) | Needs Documentation |
| scripts/agent_instantiation_guard.py | ImportRemover | __init__ | (self, classes_to_remove) | Needs Documentation |
| scripts/agent_instantiation_guard.py | ImportRemover | leave_ImportFrom | (self, original_node, updated_node) | Needs Documentation |
| scripts/check_direct_agent_instantiation.py | - | check_file | (path) | Needs Documentation |
| scripts/check_direct_agent_instantiation.py | - | is_in_test_dir | (path) | Needs Documentation |
| scripts/check_direct_agent_instantiation.py | - | main | (root_dir) | Needs Documentation |
| scripts/cli.py | - | dev_start | (dev_start) | Start the development environment using Docker Compose. |
| scripts/doc_ports.py | - | generate_table | (ports) | Needs Documentation |
| scripts/doc_ports.py | - | main | () | Needs Documentation |
| scripts/doc_ports.py | - | parse_env | () | Needs Documentation |
| scripts/doc_ports.py | - | update_doc | (table_md) | Needs Documentation |
| scripts/gen_api_doc.py | - | main | () | Needs Documentation |
| scripts/gen_env_ports.py | - | flatten_dict | (d, parent_key, sep) | Needs Documentation |
| scripts/gen_env_ports.py | - | main | () | Needs Documentation |
| scripts/gen_env_ports.py | - | strip_prefixes | (key_str) | Strips defined prefixes from the start of a key string. |
| scripts/generate_docker_env.py | - | generate_env_file | (output_path) | Needs Documentation |
| scripts/legion_codemod_context.py | CodemodContext | __init__ | (self, *args, **kwargs) | Needs Documentation |
| scripts/migrate_redis_tags.py | - | get_client | () | Needs Documentation |
| scripts/migrate_redis_tags.py | - | main | () | Needs Documentation |
| scripts/migrate_redis_tags.py | - | migrate | (client) | Needs Documentation |
| scripts/migrate_redis_tags.py | FakeRedis | __init__ | (self) | Needs Documentation |
| scripts/migrate_redis_tags.py | FakeRedis | get | (self, key) | Needs Documentation |
| scripts/migrate_redis_tags.py | FakeRedis | keys | (self, pattern) | Needs Documentation |
| scripts/migrate_redis_tags.py | FakeRedis | set | (self, key, value) | Needs Documentation |
| scripts/sync_agents_yaml.py | - | get_default_agent_config | (agent_key, class_name) | Returns a default configuration structure for a new agent. |
| scripts/sync_agents_yaml.py | - | main | () | Needs Documentation |
| scripts/sync_agents_yaml.py | - | map_agent_keys_to_class_names | () | Scans agent modules and returns a dictionary mapping agent keys |
| scripts/sync_agents_yaml.py | - | write_config_ruamel | (config_data, yaml_instance) | Writes the generated agent configurations to agents.yaml using ruamel.yaml. |
| scripts/test_agent_instantiation_guard.py | - | run_codemod_on_string | (source_code, apply_fixes) | Needs Documentation |
| scripts/test_agent_instantiation_guard.py | TestAgentInstantiationCodemod | test_apply_fix | (self) | Needs Documentation |
| scripts/test_agent_instantiation_guard.py | TestAgentInstantiationCodemod | test_class_name_to_agent_key | (self) | Needs Documentation |
| scripts/test_agent_instantiation_guard.py | TestAgentInstantiationCodemod | test_detection_only | (self) | Needs Documentation |
| scripts/test_agent_instantiation_guard.py | TestAgentInstantiationCodemod | test_ignore_non_target_imports | (self) | Needs Documentation |
| scripts/test_agent_instantiation_guard.py | TestAgentInstantiationCodemod | test_no_change_if_no_agents | (self) | Needs Documentation |
| scripts/test_agent_instantiation_guard.py | TestAgentInstantiationCodemod | test_skip_orchestrator_file | (self) | Needs Documentation |
| scripts/test_lmstudio_models.py | - | _completion_helper | (model, prompt, image) | Needs Documentation |
| scripts/test_lmstudio_models.py | - | list_models | () | Needs Documentation |
| scripts/test_lmstudio_models.py | - | main | () | Needs Documentation |
| scripts/test_lmstudio_models.py | - | test_text_model | () | Needs Documentation |
| skills/search.py | - | cosine | (a, b) | Needs Documentation |
| skills/search.py | - | search_placeholder | (query_embedding, docs, top_k) | Perform a vector similarity search over docs. |
| skills/summarize.py | - | summarize_placeholder | (snippets, model, max_tokens, temperature) | Summarize a list of memory snippets using the LLM. |
| legion/utils/http_client.py | HTTPClient | __init__ | (self, max_retries, backoff_factor, timeout) | Needs Documentation |
| legion/utils/http_client.py | HTTPClient | get | (self, path, headers) | Needs Documentation |
| legion/utils/http_client.py | HTTPClient | post | (self, path, json, headers) | Needs Documentation |
| tests/agents/test_agent_contracts.py | - | fake_call_llm | (thread_id, history, **kwargs) | Needs Documentation |
| tests/agents/test_agent_contracts.py | - | fake_post | (msg) | Needs Documentation |
| tests/agents/test_agent_contracts.py | - | test_architect_handle_review_override | (monkeypatch) | Needs Documentation |
| tests/agents/test_agent_contracts.py | - | test_prompt_builder_simple | () | Needs Documentation |
| tests/agents/test_agent_contracts.py | DummyOrch | __init__ | (self) | Needs Documentation |
| tests/agents/test_agent_contracts.py | DummyOrch | __str__ | (self) | Needs Documentation |
| tests/agents/test_agent_memory.py | - | make_agent | (agent_cls) | Needs Documentation |
| tests/agents/test_agent_memory.py | - | test_agent_memory_persistence_across_reload | () | Needs Documentation |
| tests/agents/test_agent_memory.py | - | test_agent_memory_persistence_and_retrieval | (agent_cls) | Needs Documentation |
| tests/agents/test_agent_memory.py | - | test_cross_agent_memory_isolation | () | Needs Documentation |
| tests/agents/test_agent_memory.py | DummyOrchestrator | __init__ | (self) | Needs Documentation |
| tests/agents/test_agents.py | - | test_agent_instantiation_and_properties | () | Needs Documentation |
| tests/agents/test_agents.py | - | test_base_agent_empty_input | () | Test BaseAgent's response to empty or invalid input. |
| tests/agents/test_agents.py | - | test_base_agent_error_handling | () | Test BaseAgent's error handling for unexpected issues. |
| tests/agents/test_agents.py | - | test_env | (tmp_path_factory) | Needs Documentation |
| tests/agents/test_agents.py | - | test_metrics_agent_composes_summary | (test_env, monkeypatch) | Needs Documentation |
| tests/agents/test_agents.py | - | test_metrics_agent_reads_task_log | (test_env, monkeypatch) | Needs Documentation |
| tests/agents/test_agents.py | - | test_self_assessment_scheduler_guard | (monkeypatch) | Needs Documentation |
| tests/agents/test_agents.py | - | test_therapist_agent_composes_summary | (test_env, monkeypatch) | Needs Documentation |
| tests/agents/test_agents.py | - | test_therapist_agent_reads_task_log | (test_env, monkeypatch) | Needs Documentation |
| tests/agents/test_agents.py | DummyBaseAgent | self_assess | (self) | Needs Documentation |
| tests/agents/test_agents.py | DummyClient | get_channel | (self, channel_id) | Needs Documentation |
| tests/agents/test_agents.py | DummyOrchestrator | __init__ | (self) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fail_fetch | (*a, **k) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fail_open | (*a, **kw) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fake_call_llm | (thread_id, messages, **kwargs) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fake_history | (self, channel_id, thread_id, limit) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fake_post | (msg) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fake_post | (msg) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fake_post_to_discord | (msg) | Needs Documentation |
| tests/agents/test_base_agent.py | - | fake_store | (name, mems, base_dir) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_agent_smoke_all_inherit | (monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_base_agent_custom_llm_client | () | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_base_agent_handle_message_error_branches | (monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_dispatch_message_with_context | (monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_echo_agent_handle_message_payload_and_memory | (monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_embedding_fallback | (monkeypatch, caplog) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_fetch_thread_history_empty | (monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_fetch_thread_history_error | (monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_fetch_thread_history_partial | (monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_helper_names_exist | () | Needs Documentation |
| tests/agents/test_base_agent.py | - | test_legion_agent_memory_vector_store | (tmp_path, monkeypatch) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyAgent | handle_message | (self, context, **kwargs) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyChan | history | (self, limit) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyClient | get_channel | (self, channel_id) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyClient | get_channel | (self, channel_id) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyHistory | history | (self, limit) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyHistory | history | (self, limit) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyHistory | history | (self, limit) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyLLMClient | __init__ | (self) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyLLMClient | generate | (self, *a, **k) | Needs Documentation |
| tests/agents/test_base_agent.py | DummyMsg | __init__ | (self, content) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | health_agent | (mock_orchestrator, mock_llm_client) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | mock_llm_client | () | Needs Documentation |
| tests/agents/test_healthcheck.py | - | mock_memory | () | Needs Documentation |
| tests/agents/test_healthcheck.py | - | mock_orchestrator | () | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_check_dependencies | (health_agent, mock_memory) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_error_handling | (health_agent) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_generate_report | (health_agent, mock_memory, mock_llm_client) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_get_status | (health_agent) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_health_agent_initialization | (health_agent) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_health_agent_start_stop | (health_agent) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_health_loop_above_threshold | (health_agent) | Needs Documentation |
| tests/agents/test_healthcheck.py | - | test_health_loop_below_threshold | (health_agent) | Needs Documentation |
| tests/agents/test_memory_helpers.py | - | agent | () | Needs Documentation |
| tests/agents/test_memory_helpers.py | - | fake_retrieve | (agent_name, embedding, top_k, base_dir) | Needs Documentation |
| tests/agents/test_memory_helpers.py | - | fake_store | (agent_name, snippets, base_dir) | Needs Documentation |
| tests/agents/test_memory_helpers.py | - | test_mem_retrieve_calls_underlying_with_correct_args | (monkeypatch, agent) | Needs Documentation |
| tests/agents/test_memory_helpers.py | - | test_mem_store_dedup_and_enrichment | (monkeypatch, agent) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | - | fail_create | (**kwargs) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | - | fake_create | (**kwargs) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | - | fake_get | (url, timeout) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | - | test_placeholder_indexing | () | Needs Documentation |
| tests/agents/test_skills_and_utils.py | - | test_placeholder_network | (monkeypatch) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | - | test_search_placeholder_basic | () | Needs Documentation |
| tests/agents/test_skills_and_utils.py | - | test_summarize_placeholder | (monkeypatch) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | Choice | __init__ | (self, content) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | DummyResp | __init__ | (self, code) | Needs Documentation |
| tests/agents/test_skills_and_utils.py | DummyResp | __init__ | (self, content) | Needs Documentation |
| tests/agents/test_therapist_validation.py | - | fake_handle_message | (**kwargs) | Needs Documentation |
| tests/agents/test_therapist_validation.py | - | fake_post | (msg) | Needs Documentation |
| tests/agents/test_therapist_validation.py | - | test_therapist_validate_request_and_fallback | (monkeypatch) | Needs Documentation |
| tests/api/v1/test_api_agents.py | - | test_assess_agent_no_permission | (client, normal_user_token_headers) | Test triggering self-assessment without superuser permissions. |
| tests/api/v1/test_api_agents.py | - | test_assess_agent_not_found | (client, superuser_token_headers) | Test triggering self-assessment for a non-existent agent. |
| tests/api/v1/test_api_agents.py | - | test_assess_agent_success | (client, superuser_token_headers) | Test triggering self-assessment for an agent successfully (mocked orchestrator). |
| tests/api/v1/test_api_agents.py | - | test_dispatch_message_not_found | (client, normal_user_token_headers) | Test dispatching a message to a non-existent agent. |
| tests/api/v1/test_api_agents.py | - | test_dispatch_message_success | (client, normal_user_token_headers) | Test dispatching a message to an agent successfully (mocked orchestrator). |
| tests/api/v1/test_api_agents.py | - | test_get_agent_config | (mock_send_request, agent_name, mock_response, expected_status, expected_json) | Tests GET /agents/{agent_name}/config endpoint. |
| tests/api/v1/test_api_agents.py | - | test_get_agent_status | (mock_send_request, agent_name, mock_response, expected_status, expected_json) | Tests GET /agents/{agent_name} endpoint. |
| tests/api/v1/test_api_agents.py | - | test_list_agents | (mock_send_request, mock_response, expected_status, expected_json) | Tests GET /agents endpoint. |
| tests/api/v1/test_api_agents.py | - | test_reload_configs_no_permission | (client, normal_user_token_headers) | Test reloading configs without superuser permissions. |
| tests/api/v1/test_api_agents.py | - | test_reload_configs_orchestrator_error | (client, superuser_token_headers) | Test orchestrator error during reload configs. |
| tests/api/v1/test_api_agents.py | - | test_reload_configs_success | (client, superuser_token_headers) | Test reloading agent configs successfully (mocked orchestrator). |
| tests/api/v1/test_api_agents.py | - | test_restart_agent_success | (client, superuser_token_headers) | Test restarting an agent successfully. |
| tests/api/v1/test_api_agents.py | - | test_start_agent_no_permission | (client, normal_user_token_headers) | Test starting agent without superuser permissions. |
| tests/api/v1/test_api_agents.py | - | test_start_agent_not_found | (client, superuser_token_headers) | Test starting an agent that doesn't exist. |
| tests/api/v1/test_api_agents.py | - | test_start_agent_orchestrator_error | (client, superuser_token_headers) | Test orchestrator error when starting agent. |
| tests/api/v1/test_api_agents.py | - | test_start_agent_success | (client, superuser_token_headers) | Test starting an agent successfully (mocked orchestrator). |
| tests/api/v1/test_api_agents.py | - | test_stop_agent_success | (client, superuser_token_headers) | Test stopping an agent successfully. |
| tests/api/v1/test_api_agents.py | - | test_update_agent_config_no_permission | (client, normal_user_token_headers) | Test updating agent configuration without superuser permissions. |
| tests/api/v1/test_api_agents.py | - | test_update_agent_config_not_found | (client, superuser_token_headers) | Test updating configuration for a non-existent agent. |
| tests/api/v1/test_api_agents.py | - | test_update_agent_config_success | (client, superuser_token_headers) | Test updating agent configuration successfully (mocked orchestrator). |
| tests/api/v1/test_auth.py | - | test_get_current_user | (client, normal_user_token_headers) | Test getting the current user. |
| tests/api/v1/test_auth.py | - | test_get_user_preferences | (client, normal_user_token_headers, db) | Test getting user preferences (should create defaults if none exist). |
| tests/api/v1/test_auth.py | - | test_login_access_token | (client, db) | Test getting an access token via form data. |
| tests/api/v1/test_auth.py | - | test_login_incorrect_password | (client, db) | Test login with incorrect password. |
| tests/api/v1/test_auth.py | - | test_logout | (client, normal_user_token_headers) | Test the placeholder logout endpoint. |
| tests/api/v1/test_auth.py | - | test_register_existing_username | (client, db) | Test registration with an existing username. |
| tests/api/v1/test_auth.py | - | test_register_user | (client, db) | Test user registration. |
| tests/api/v1/test_auth.py | - | test_update_user_preferences | (client, normal_user_token_headers, db) | Test updating user preferences. |
| tests/api/v1/test_system.py | - | test_get_memory_stats_orchestrator_error | (client, normal_user_token_headers, mocker) | Test orchestrator error when getting memory stats. |
| tests/api/v1/test_system.py | - | test_get_memory_stats_success | (client, normal_user_token_headers, mocker) | Test successful retrieval of memory stats. |
| tests/api/v1/test_system.py | - | test_get_memory_stats_timeout | (client, normal_user_token_headers, mocker) | Test timeout when getting memory stats. |
| tests/api/v1/test_system.py | - | test_get_system_logs | (client, normal_user_token_headers, mocker) | Needs Documentation |
| tests/api/v1/test_system.py | - | test_get_system_metrics | (client, normal_user_token_headers, mocker) | Needs Documentation |
| tests/api/v1/test_system.py | - | test_get_system_status | (client, normal_user_token_headers, mocker) | Needs Documentation |
| tests/api/v1/test_system.py | - | test_get_system_status_error | (client, normal_user_token_headers, mocker) | Needs Documentation |
| tests/api/v1/test_system.py | - | test_get_system_status_timeout | (client, normal_user_token_headers, mocker) | Needs Documentation |
| tests/api/v1/test_tasks.py | - | test_delete_task_failure | (mock_cancel, client, normal_user_token_headers) | Test task cancellation failure. |
| tests/api/v1/test_tasks.py | - | test_delete_task_success | (mock_cancel, client, normal_user_token_headers) | Test successful task cancellation. |
| tests/api/v1/test_tasks.py | - | test_delete_task_unauthorized | (client) | Test cancelling a task without auth. |
| tests/api/v1/test_tasks.py | - | test_get_tasks_failure | (mock_list, client, normal_user_token_headers) | Test listing tasks failure. |
| tests/api/v1/test_tasks.py | - | test_get_tasks_success | (mock_list, client, normal_user_token_headers) | Test listing tasks successfully. |
| tests/api/v1/test_tasks.py | - | test_get_tasks_unauthorized | (client) | Test listing tasks without auth. |
| tests/api/v1/test_tasks.py | - | test_post_task_failure | (mock_create, client, normal_user_token_headers) | Test task submission failure. |
| tests/api/v1/test_tasks.py | - | test_post_task_success | (mock_create, client, normal_user_token_headers) | Test successful task submission. |
| tests/api/v1/test_tasks.py | - | test_post_task_unauthorized | (client) | Test submitting task without auth. |
| tests/api/v1/test_tasks.py | - | test_read_task_not_found | (mock_get, client, normal_user_token_headers) | Test retrieving a non-existent task. |
| tests/api/v1/test_tasks.py | - | test_read_task_success | (mock_get, client, normal_user_token_headers) | Test retrieving a task successfully. |
| tests/cli/test_cli.py | - | mock_orchestrator | (monkeypatch) | Needs Documentation |
| tests/cli/test_cli.py | - | test_list_agents | (capsys) | Needs Documentation |
| tests/cli/test_cli.py | - | test_ports | (capsys) | Needs Documentation |
| tests/cli/test_cli.py | - | test_run_agent_success | (capsys, key, msg) | Needs Documentation |
| tests/cli/test_cli.py | - | test_run_agent_unknown | (capsys) | Needs Documentation |
| tests/cli/test_cli.py | - | test_show_config | (capsys) | Needs Documentation |
| tests/cli/test_cli.py | - | test_version | (capsys, monkeypatch) | Needs Documentation |
| tests/cli/test_cli.py | FakeOrchestrator | __init__ | (self, *args, **kwargs) | Needs Documentation |
| tests/cli/test_cli.py | FakeOrchestrator | dispatch | (self, key, payload) | Needs Documentation |
| tests/cli/test_cli.py | FakeOrchestrator | load_agent | (self, key) | Needs Documentation |
| tests/conftest.py | - | dummy_orchestrator | () | Needs Documentation |
| tests/conftest.py | DummyClient | __init__ | (self) | Needs Documentation |
| tests/conftest.py | DummyOrch | __init__ | (self) | Needs Documentation |
| tests/conftest.py | DummyUser | __init__ | (self, id_val) | Needs Documentation |
| tests/core/test_chroma_client.py | - | fake_create | (model, input_text) | Needs Documentation |
| tests/core/test_chroma_client.py | - | fake_upsert | (ids, embeddings, metadatas, documents) | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_compute_similarity_correct | () | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_compute_similarity_raises_not_implemented | () | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_compute_similarity_zero_vector | () | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_create_embedding_empty_text_error | () | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_create_embedding_invokes_openai | (monkeypatch) | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_query_embeddings_raises_not_implemented | () | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_retrieve_similar_embeddings_empty_query_error | () | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_retrieve_similar_embeddings_filters_threshold | () | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_store_embedding_calls_upsert | (monkeypatch) | Needs Documentation |
| tests/core/test_chroma_client.py | - | test_store_embedding_invalid_inputs | () | Needs Documentation |
| tests/core/test_chroma_client.py | DummyCollection | __init__ | (self, result) | Needs Documentation |
| tests/core/test_chroma_client.py | DummyCollection | query | (self, query_embeddings, n_results, include_embeddings, include_distances) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | middleware | (mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | mock_chroma_client | () | Needs Documentation |
| tests/core/test_middleware_directive.py | - | mock_directive_compliance | () | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_directive_non_compliant | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_directive_rejection_takes_precedence | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_directive_therapist_takes_precedence | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_directive_therapist_takes_precedence_over_embedding_review | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_directive_therapist_triggered | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_embedding_creation_fails | (middleware, mock_chroma_client) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_empty_text | (middleware) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_no_similar_embeddings | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_retrieval_fails | (middleware, mock_chroma_client) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_similarity_acceptable | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_similarity_escalate_therapist | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_similarity_needs_review | (middleware, mock_chroma_client, mock_directive_compliance) | Needs Documentation |
| tests/core/test_middleware_directive.py | - | test_process_request_similarity_rejected | (middleware, mock_chroma_client) | Needs Documentation |
| tests/core/test_network.py | - | test_fetch_with_retries_all_fail | (mock_sleep, mock_get) | Test fetch fails after all retries. |
| tests/core/test_network.py | - | test_fetch_with_retries_fail_then_success | (mock_sleep, mock_get) | Test successful fetch after one retry. |
| tests/core/test_network.py | - | test_fetch_with_retries_success | (mock_get) | Test successful fetch after no retries. |
| tests/discord/test_commands.py | - | fake_log | (msg) | Needs Documentation |
| tests/discord/test_commands.py | - | fake_log | (msg) | Needs Documentation |
| tests/discord/test_commands.py | - | fake_log | (msg) | Needs Documentation |
| tests/discord/test_commands.py | - | fake_log | (msg) | Needs Documentation |
| tests/discord/test_commands.py | - | test_alert_subscribe | (monkeypatch) | Needs Documentation |
| tests/discord/test_commands.py | - | test_config_agent_parsing_and_call | (monkeypatch) | Needs Documentation |
| tests/discord/test_commands.py | - | test_feedback_parsing_and_call | (monkeypatch) | Needs Documentation |
| tests/discord/test_commands.py | - | test_state_query_parsing_and_call | (monkeypatch) | Needs Documentation |
| tests/discord/test_commands.py | DummyChan | send | (self, *args, **kwargs) | Needs Documentation |
| tests/discord/test_commands.py | DummyChan | send | (self, *args, **kwargs) | Needs Documentation |
| tests/discord/test_commands.py | DummyContext | __init__ | (self) | Needs Documentation |
| tests/discord/test_commands.py | DummyContext | send | (self, *args, **kwargs) | Needs Documentation |
| tests/discord/test_create_task_command.py | - | bot_and_cog | (monkeypatch) | Needs Documentation |
| tests/discord/test_create_task_command.py | - | test_create_task_failure_from_orchestrator_direct_call | (bot_and_cog) | Needs Documentation |
| tests/discord/test_create_task_command.py | - | test_create_task_other_exception_direct_call | (bot_and_cog) | Needs Documentation |
| tests/discord/test_create_task_command.py | - | test_create_task_success_direct_call | (bot_and_cog) | Needs Documentation |
| tests/discord/test_create_task_command.py | MockAuthor | __init__ | (self, name, id) | Needs Documentation |
| tests/discord/test_create_task_command.py | MockCtx | __init__ | (self) | Needs Documentation |
| tests/discord/test_create_task_command.py | MockCtx | send | (self, content, embed) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | bot | (monkeypatch) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | fetch_last_message | (channel) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | guild | () | Needs Documentation |
| tests/discord/test_discord_integration.py | - | test_alert_subscribe_and_alert_flow | (bot, guild) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | test_config_agent_slash_command | (bot, guild) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | test_error_handling_invalid_args | (bot, guild) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | test_feedback_slash_command | (bot, guild) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | test_message_event_flow | (bot, guild) | Needs Documentation |
| tests/discord/test_discord_integration.py | - | test_state_query_slash_command | (bot, guild) | Needs Documentation |
| tests/discord/test_discord_integration.py | DummyCtx | __init__ | (self) | Needs Documentation |
| tests/discord/test_discord_integration.py | DummyCtx | __init__ | (self) | Needs Documentation |
| tests/discord/test_discord_integration.py | DummyCtx | __init__ | (self) | Needs Documentation |
| tests/discord/test_discord_integration.py | DummyCtx | __init__ | (self) | Needs Documentation |
| tests/discord/test_discord_integration.py | DummyCtx | __init__ | (self) | Needs Documentation |
| tests/discord/test_health_cog.py | - | health_agent | (mock_channel, mock_memory) | Needs Documentation |
| tests/discord/test_health_cog.py | - | health_cog | (event_loop) | Needs Documentation |
| tests/discord/test_health_cog.py | - | mock_channel | () | Needs Documentation |
| tests/discord/test_health_cog.py | - | mock_memory | () | Needs Documentation |
| tests/discord/test_health_cog.py | - | test_health_agent_initialization | (health_agent) | Test health agent initializes with correct start time. |
| tests/discord/test_health_cog.py | - | test_health_agent_start | (health_agent) | Test health agent start creates background task. |
| tests/discord/test_health_cog.py | - | test_health_command | (health_cog) | Test the !health command (currently placeholder). |
| tests/discord/test_health_cog.py | - | test_health_loop_above_threshold | (health_agent) | Test health loop behavior when uptime is above threshold. |
| tests/discord/test_health_cog.py | - | test_health_loop_below_threshold | (health_agent) | Test health loop behavior when uptime is below threshold. |
| tests/discord/test_health_cog.py | - | test_health_loop_interval | (health_agent) | Test health loop respects the configured interval. |
| tests/discord/test_health_cog.py | - | test_ping_command | (health_cog) | Test the !ping command for latency calculation. |
| tests/discord/test_health_cog.py | MockBot | __init__ | (self, *args, **kwargs) | Needs Documentation |
| tests/discord/test_health_cog.py | MockContext | send | (self, *args, **kwargs) | Needs Documentation |
| tests/discord/test_orchestrator_cog.py | - | mock_bot | () | Needs Documentation |
| tests/discord/test_orchestrator_cog.py | - | mock_interaction | () | Needs Documentation |
| tests/discord/test_orchestrator_cog.py | - | orchestrator_cog | (mock_bot) | Needs Documentation |
| tests/discord/test_orchestrator_cog.py | - | test_ask_command_invalid_agent | (orchestrator_cog, mock_interaction) | Test the /ask slash command with an invalid agent name. |
| tests/discord/test_orchestrator_cog.py | - | test_ask_command_success | (orchestrator_cog, mock_interaction) | Test the /ask slash command with a valid agent. |
| tests/discord/test_orchestrator_cog.py | - | test_reload_configs_command | (orchestrator_cog, mock_interaction) | Test the /reload_configs slash command. |
| tests/discord/test_ux_feed.py | - | mock_channel | () | Needs Documentation |
| tests/discord/test_ux_feed.py | - | test_message_type_enum | () | Test MessageType enum values. |
| tests/discord/test_ux_feed.py | - | test_render_error | () | Test error message rendering. |
| tests/discord/test_ux_feed.py | - | test_render_info | () | Test info message rendering. |
| tests/discord/test_ux_feed.py | - | test_render_message_all_types | () | Test render_message with all message types. |
| tests/discord/test_ux_feed.py | - | test_render_message_invalid_type | () | Test render_message with invalid message type. |
| tests/discord/test_ux_feed.py | - | test_render_success | () | Test success message rendering. |
| tests/discord/test_ux_feed.py | - | test_render_warning | () | Test warning message rendering. |
| tests/helpers/stub_llm.py | StubLLMClient | create | (self, payload) | Simulate an LLM create call by returning status ok and echoing payload. |
| tests/integration/conftest.py | - | agent_keys | () | Provides a list of expected agent keys for tests like agent_roundtrip. |
| tests/integration/conftest.py | - | minimal_agent_config | (tmp_path) | Needs Documentation |
| tests/integration/conftest.py | - | mock_llm_client_instance | () | Needs Documentation |
| tests/integration/conftest.py | - | orchestrator | (minimal_agent_config, setup_di_container) | Provides an Orchestrator instance with minimal config and mocked dependencies. |
| tests/integration/conftest.py | - | setup_di_container | (state_manager_instance, mock_llm_client_instance) | Automatically registers mock instances in the DI container for integration [...] |
| tests/integration/conftest.py | - | state_manager_instance | (tmp_path) | Needs Documentation |
| tests/integration/conftest.py | - | task_name | (task_item) | Needs Documentation |
| tests/integration/conftest.py | MockLLMClient | __init__ | (self) | Needs Documentation |
| tests/integration/conftest.py | MockLLMClient | call | (self, messages, **kwargs) | Needs Documentation |
| tests/integration/conftest.py | MockLLMClient | get_embedding | (self, text) | Needs Documentation |
| tests/integration/test_agent_roundtrip.py | - | test_agent_roundtrip | (orchestrator, agent_keys, tmp_path) | For each agent key, ensure load_agent and dispatch round-trip works and [...] |
| tests/integration/test_discord_end_to_end.py | - | test_config_command_end_to_end | (monkeypatch) | Needs Documentation |
| tests/integration/test_discord_end_to_end.py | DummyChannel | __init__ | (self) | Needs Documentation |
| tests/integration/test_discord_end_to_end.py | DummyChannel | send | (self, msg) | Needs Documentation |
| tests/integration/test_discord_end_to_end.py | DummyConfigChan | send | (self, *args, **kwargs) | Needs Documentation |
| tests/integration/test_discord_end_to_end.py | DummyContext | __init__ | (self, channel) | Needs Documentation |
| tests/integration/test_discord_end_to_end.py | DummyContext | send | (self, *args, **kwargs) | Needs Documentation |
| tests/integration/test_orchestrator_bench.py | - | asyncio_benchmark_wrapper | (async_fn) | Wraps an async function for pytest-benchmark. |
| tests/integration/test_orchestrator_bench.py | - | asyncio_run | (coro) | Needs Documentation |
| tests/integration/test_orchestrator_bench.py | - | dispatch_once | () | Needs Documentation |
| tests/integration/test_orchestrator_bench.py | - | runner | () | Needs Documentation |
| tests/integration/test_orchestrator_bench.py | - | test_dispatch_throughput_benchmark | (benchmark, monkeypatch, tmp_path) | Needs Documentation |
| tests/integration/test_orchestrator_bench.py | - | test_llm_latency_benchmark | (benchmark, monkeypatch) | Needs Documentation |
| tests/integration/test_orchestrator_bench.py | FastMockLLMClient | call | (self, messages, **kwargs) | Needs Documentation |
| tests/integration/test_orchestrator_bench.py | FastMockLLMClient | get_embedding | (self, text) | Needs Documentation |
| tests/integration/test_orchestrator_dispatch.py | - | test_dispatch_message_integration | (test_env, monkeypatch) | Tests the orchestrator dispatch flow, including state logging and telemetry. |
| tests/integration/test_orchestrator_dispatch.py | - | test_env | (tmp_path) | Provides a temporary environment with isolated state directory. |
| tests/integration/test_orchestrator_dispatch.py | MockLLMClient | call | (self, messages, **kwargs) | Needs Documentation |
| tests/integration/test_orchestrator_dispatch.py | MockLLMClient | get_embedding | (self, text) | Needs Documentation |
| tests/integration/test_orchestrator_end_to_end.py | - | fake_post | (msg) | Needs Documentation |
| tests/integration/test_orchestrator_end_to_end.py | - | fake_post | (msg) | Needs Documentation |
| tests/integration/test_orchestrator_end_to_end.py | - | test_orchestrator_dispatch_happy_path | (monkeypatch) | Needs Documentation |
| tests/integration/test_orchestrator_end_to_end.py | - | test_orchestrator_dispatch_validation_failure | (monkeypatch) | Needs Documentation |
| tests/integration/test_orchestrator_end_to_end.py | DummyLLM | __call__ | (self, thread_id, history, **kwargs) | Needs Documentation |
| tests/integration/test_orchestrator_end_to_end.py | DummyLLM | __init__ | (self) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | - | mock_dependencies | () | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | - | mock_error_handle_task | (payload) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | - | mock_load_agent_configs_side_effect | (self_orch_param) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | - | mock_success_handle_task | (payload) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | - | orchestrator_instance | (mock_dependencies) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | - | test_ask_agent_exception | (orchestrator_instance, caplog) | Test exception handling in the 'ask' method when an agent fails. |
| tests/integration/test_orchestrator_errors.py | - | test_broadcast_with_agent_exception | (orchestrator_instance, caplog) | Test exception handling in the 'broadcast' method when an agent fails. |
| tests/integration/test_orchestrator_errors.py | - | test_dispatch_message_agent_exception | (orchestrator_instance, caplog) | Test exception handling when an agent's handle_task raises an error during [...] |
| tests/integration/test_orchestrator_errors.py | - | test_dispatch_message_unknown_agent | (orchestrator_instance, caplog) | Test dispatch_message with an unknown agent name. |
| tests/integration/test_orchestrator_errors.py | - | test_middleware_error_handling_in_dispatch_message | (orchestrator_instance, caplog) | Test dispatch_message when run_middleware_pipeline raises an exception. |
| tests/integration/test_orchestrator_errors.py | - | test_orchestrator_startup_and_shutdown | (orchestrator_instance) | Test basic startup and graceful shutdown of the orchestrator. |
| tests/integration/test_orchestrator_errors.py | - | test_shutdown_cancels_background_tasks | (orchestrator_instance) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | - | test_zmq_rep_loop_dispatch_command_exception | (orchestrator_instance, caplog) | Test _zmq_rep_loop handling when dispatch_command raises an exception. |
| tests/integration/test_orchestrator_errors.py | - | test_zmq_rep_loop_json_decode_error | (orchestrator_instance, caplog) | Test _zmq_rep_loop handling of JSONDecodeError. |
| tests/integration/test_orchestrator_errors.py | MockAgent | __init__ | (self, name, config, orchestrator_ref, llm_client) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | MockAgent | handle_task | (self, payload) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | MockAgent | is_shutdown | (self) | Needs Documentation |
| tests/integration/test_orchestrator_errors.py | MockAgent | shutdown | (self) | Needs Documentation |
| tests/integration/test_orchestrator_security.py | - | test_orchestrator_rejects_dangerous_command | (monkeypatch) | Needs Documentation |
| tests/test_agent_capabilities.py | - | test_capability_mapping_matches_contracts | () | Needs Documentation |
| tests/test_architect_agent.py | - | fake_post_to_discord | (self, message) | Needs Documentation |
| tests/test_architect_agent.py | - | fake_post_to_discord | (self, message) | Needs Documentation |
| tests/test_architect_agent.py | - | fake_post_to_discord | (self, message) | Needs Documentation |
| tests/test_architect_agent.py | - | test_A1_architect_reads_task_log | (test_env, monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_A2_architect_extracts_llm_metrics | (test_env, monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_A3_architect_composes_summary | (test_env, monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_A4_architect_posts_summary | (test_env, monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_A5_architect_no_logs_fallback | (test_env, monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_B1_architect_tags_metrics | (monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_B2_architect_triggers_therapist | (monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_C1_architect_end_to_end | (monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_C2_llm_api_downtime | (monkeypatch) | Needs Documentation |
| tests/test_architect_agent.py | - | test_D1_db_memory_entries | (test_env) | Needs Documentation |
| tests/test_architect_agent.py | - | test_D2_log_offsets_advance | (test_env) | Needs Documentation |
| tests/test_architect_agent.py | - | test_env | (tmp_path_factory) | Needs Documentation |
| tests/test_architect_agent.py | DummyClient | get_channel | (self, channel_id) | Needs Documentation |
| tests/test_discord_message_sending.py | - | test_send_agent_message | () | Needs Documentation |
| tests/test_http_client.py | - | dummy_session | (monkeypatch) | Needs Documentation |
| tests/test_http_client.py | - | env_vars | (monkeypatch) | Needs Documentation |
| tests/test_http_client.py | - | test_http_get | (dummy_session) | Needs Documentation |
| tests/test_http_client.py | - | test_http_post | (dummy_session) | Needs Documentation |
| tests/test_http_client.py | DummyResp | __init__ | (self, data) | Needs Documentation |
| tests/test_http_client.py | DummyResp | json | (self) | Needs Documentation |
| tests/test_http_client.py | DummyResp | raise_for_status | (self) | Needs Documentation |
| tests/test_http_client.py | Session | get | (self, url, headers, timeout) | Needs Documentation |
| tests/test_http_client.py | Session | post | (self, url, json, headers, timeout) | Needs Documentation |
| tests/test_interface.py | - | client | () | Needs Documentation |
| tests/test_interface.py | - | db_session | () | Needs Documentation |
| tests/test_interface.py | - | regular_user_token_headers | (client, db_session) | Needs Documentation |
| tests/test_interface.py | - | superuser_token_headers | (client, db_session) | Needs Documentation |
| tests/test_interface.py | - | test_create_agent_by_regular_user | (client, regular_user_token_headers) | Test creating an agent fails for a regular user. |
| tests/test_interface.py | - | test_create_agent_by_superuser | (client, superuser_token_headers) | Test creating an agent as a superuser. |
| tests/test_interface.py | - | test_delete_agent_by_regular_user_forbidden | (client, regular_user_token_headers, superuser_token_headers) | Test deleting an agent as a regular user is forbidden. |
| tests/test_interface.py | - | test_delete_agent_by_superuser | (client, superuser_token_headers) | Test deleting an agent as a superuser. |
| tests/test_interface.py | - | test_delete_nonexistent_agent | (client, superuser_token_headers) | Test deleting a non-existent agent returns 404. |
| tests/test_interface.py | - | test_dispatch_message_agent_not_found | (client, regular_user_token_headers, mocker) | Test dispatching a message to an agent that doesn't exist. |
| tests/test_interface.py | - | test_dispatch_message_orchestrator_error | (client, regular_user_token_headers, mocker) | Test handling an orchestrator error during dispatch. |
| tests/test_interface.py | - | test_dispatch_message_success | (client, regular_user_token_headers, mocker) | Test successfully dispatching a message to an agent. |
| tests/test_interface.py | - | test_dispatch_message_unauthorized | (client) | Test dispatching a message without authentication. |
| tests/test_interface.py | - | test_get_orchestrator_status_error_response | (mock_call_orchestrator, client, regular_user_token_headers) | Test orchestrator returning an error status. |
| tests/test_interface.py | - | test_get_orchestrator_status_send_error | (mock_call_orchestrator, client, regular_user_token_headers) | Test scenario where _call_orchestrator itself raises an unexpected error [...] |
| tests/test_interface.py | - | test_get_orchestrator_status_success | (mock_call_orchestrator, client, regular_user_token_headers) | Test successful retrieval of orchestrator status. |
| tests/test_interface.py | - | test_get_orchestrator_status_timeout | (mock_call_orchestrator, client, regular_user_token_headers) | Test orchestrator status retrieval timeout. |
| tests/test_interface.py | - | test_get_orchestrator_status_unauthenticated | (client) | Test accessing orchestrator status endpoint without authentication. |
| tests/test_interface.py | - | test_get_system_logs_error_response | (mock_call_orchestrator, client, regular_user_token_headers) | Test system logs retrieval with orchestrator error. |
| tests/test_interface.py | - | test_get_system_logs_send_error | (mock_call_orchestrator, client, regular_user_token_headers) | Test scenario where _call_orchestrator itself raises an unexpected error [...] |
| tests/test_interface.py | - | test_get_system_logs_success | (mock_call_orchestrator, client, regular_user_token_headers) | Test successfully retrieving system logs via IPC. |
| tests/test_interface.py | - | test_get_system_logs_timeout | (mock_call_orchestrator, client, regular_user_token_headers) | Test system logs retrieval timeout. |
| tests/test_interface.py | - | test_get_system_logs_unauthenticated | (client) | Test accessing system logs endpoint without authentication. |
| tests/test_interface.py | - | test_get_system_metrics_success | (mock_call_orchestrator, client, regular_user_token_headers) | Test successfully getting system metrics via IPC. |
| tests/test_interface.py | - | test_get_system_metrics_timeout | (mock_call_orchestrator, client, regular_user_token_headers) | Test system metrics retrieval timeout. |
| tests/test_interface.py | - | test_get_system_metrics_unauthenticated | (client) | Test accessing system metrics endpoint without authentication. |
| tests/test_interface.py | - | test_list_agents_authenticated | (client, regular_user_token_headers) | Test accessing /agents endpoint with valid regular user authentication. |
| tests/test_interface.py | - | test_list_agents_unauthenticated | (client) | Test accessing /agents endpoint without authentication. |
| tests/test_interface.py | - | test_login_user_incorrect_password | (client) | Test login attempt with incorrect password. |
| tests/test_interface.py | - | test_login_user_nonexistent_username | (client) | Test login attempt with a username that does not exist. |
| tests/test_interface.py | - | test_login_user_success | (client) | Test successful user login and token retrieval. |
| tests/test_interface.py | - | test_me_endpoint_authenticated | (client) | Test accessing /me endpoint with valid authentication. |
| tests/test_interface.py | - | test_me_endpoint_unauthenticated | (client) | Test accessing /me endpoint without authentication. |
| tests/test_interface.py | - | test_read_agent_by_regular_user | (client, superuser_token_headers, regular_user_token_headers) | Test reading a specific agent as a regular user. |
| tests/test_interface.py | - | test_read_nonexistent_agent | (client, regular_user_token_headers) | Test reading a non-existent agent returns 404. |
| tests/test_interface.py | - | test_register_user | (client) | Ensure a user can register successfully. |
| tests/test_interface.py | - | test_trigger_agent_assessment_agent_not_found | (client, superuser_token_headers, mocker) | Test triggering assessment for a non-existent agent returns 404. |
| tests/test_interface.py | - | test_trigger_agent_assessment_forbidden | (client, regular_user_token_headers) | Test that a regular user cannot trigger agent assessment (403/400). |
| tests/test_interface.py | - | test_trigger_agent_assessment_orchestrator_error | (client, superuser_token_headers, mocker) | Test orchestrator error during assessment trigger returns 502. |
| tests/test_interface.py | - | test_trigger_agent_assessment_success | (client, superuser_token_headers, mocker) | Test successfully triggering agent self-assessment as superuser. |
| tests/test_interface.py | - | test_update_agent_by_regular_user_forbidden | (client, regular_user_token_headers, superuser_token_headers) | Test updating an agent as a regular user is forbidden. |
| tests/test_interface.py | - | test_update_agent_by_superuser | (client, superuser_token_headers) | Test updating an agent as a superuser. |
| tests/test_interface.py | - | test_update_agent_name_conflict | (client, superuser_token_headers) | Test updating an agent to a name that already exists returns 409. |
| tests/test_interface.py | - | test_update_nonexistent_agent | (client, superuser_token_headers) | Test updating a non-existent agent returns 404. |
| tests/test_interface.py | - | unique_user_data | (prefix) | Generates unique user data for tests. |
| tests/test_llm_connector.py | - | test_llm_generate_lmstudio | (monkeypatch) | Needs Documentation |
| tests/test_llm_connector.py | - | test_llm_generate_openai | (monkeypatch) | Needs Documentation |
| tests/test_llm_connector.py | - | test_llm_local_smoke | () | Needs Documentation |
| tests/test_llm_connector.py | FakeResp | __init__ | (self) | Needs Documentation |
| tests/test_orchestrator.py | - | test_agent_channel_ids_not_empty | () | Needs Documentation |
| tests/test_orchestrator.py | - | test_duplicate_startup_and_cleanup | (monkeypatch, caplog) | Needs Documentation |
| tests/test_orchestrator.py | - | test_orchestrator_agent_interaction | () | Test interaction between orchestrator and multiple agents. |
| tests/test_orchestrator.py | - | test_orchestrator_custom_dependencies | () | Needs Documentation |
| tests/test_orchestrator.py | - | test_orchestrator_error_handling | () | Test orchestrator's error handling for invalid agent or message. |
| tests/test_orchestrator.py | - | test_unknown_config_key_logs_warning | (tmp_path, caplog, monkeypatch) | Needs Documentation |
| tests/test_orchestrator.py | DummyLLMClient | __init__ | (self) | Needs Documentation |
| tests/test_orchestrator.py | DummyLLMClient | generate | (self, *a, **k) | Needs Documentation |
| tests/test_orchestrator.py | DummyStateManager | __init__ | (self) | Needs Documentation |
| tests/test_orchestrator.py | DummyStateManager | log_task | (self, task) | Needs Documentation |
| tests/test_orchestrator_load_agent.py | MockOrchestrator | __init__ | (self, state_manager, llm_client) | Needs Documentation |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | setUp | (self) | Set up test fixtures before each test. |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | test_caching_behavior | (self, mock_import) | Test that two calls to load_agent return the same instance (from cache). |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | test_ci_smoke_check | (self, mock_import) | Test all agent keys in the config to verify they can be loaded without error. |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | test_class_not_found | (self, mock_import) | Test that load_agent raises AgentLoadError when the agent class is not found. |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | test_import_failure | (self, mock_import) | Test that load_agent raises AgentLoadError when import fails. |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | test_instantiation_failure | (self, mock_import) | Test that load_agent raises AgentLoadError when instantiation fails. |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | test_successful_load | (self, mock_import) | Test that load_agent successfully loads and returns an agent instance. |
| tests/test_orchestrator_load_agent.py | TestOrchestratorLoadAgent | test_unknown_key | (self) | Test that load_agent raises KeyError for unknown agent keys. |
| tests/test_orchestrator_lock.py | - | test_orchestrator_duplicate_lock | (tmp_path, monkeypatch) | Needs Documentation |
| tests/test_orchestrator_ports.py | - | reset_runtime_ports | () | Needs Documentation |
| tests/test_orchestrator_ports.py | - | test_orchestrator_startup_logs_banner | (mock_logger, tmp_path) | Test that orchestrator logs the port banner when LEGION_DEBUG_PORTS is true. |
| tests/test_orchestrator_ports.py | - | test_orchestrator_startup_no_banner_if_debug_false | (mock_logger, tmp_path) | Test that orchestrator does NOT log the port banner when [...] |
| tests/test_orchestrator_ports.py | - | test_port_loading_no_env_file | () | Test that defaults are used if .env.ports does not exist. |
| tests/test_orchestrator_ports.py | - | test_port_loading_with_empty_env_file | (tmp_path) | Test that defaults are used if .env.ports is empty or has no valid entries. |
| tests/test_orchestrator_ports.py | - | test_port_loading_with_valid_env_file | (tmp_path) | Test that .env.ports overrides defaults and handles some invalid lines. |
| tests/test_redis_migration.py | - | test_migrate_adds_fields | () | Needs Documentation |
| tests/test_routing_map.py | - | test_rebuild_and_lookup | () | Needs Documentation |
| tests/test_state_repository.py | - | test_add_and_retrieve_task | () | Needs Documentation |
| tests/test_state_repository.py | - | test_update_task_status | () | Needs Documentation |
| tests/test_tag_middleware.py | - | dummy | (payload) | Needs Documentation |
| tests/test_tag_middleware.py | - | test_tag_payload_decorator | () | Needs Documentation |
| tests/test_task_registry_api.py | - | test_create_and_get_task | () | Needs Documentation |
| tests/test_task_registry_api.py | - | test_delete_task | () | Needs Documentation |
| tests/test_task_registry_api.py | - | test_filter_tasks | () | Needs Documentation |
| tests/test_websockets.py | - | test_websocket_broadcast | (client) | Test broadcasting a message to connected clients. |
| tests/test_websockets.py | - | test_websocket_connect_disconnect | (client) | Test WebSocket connection and disconnection via /ws/events. |
| tests/test_websockets.py | - | test_websocket_multiple_connections | (client) | Test handling multiple concurrent WebSocket connections. |
| tests/utils.py | - | random_email | () | Needs Documentation |
| tests/utils.py | - | random_lower_string | (length) | Needs Documentation |
| tests/utils/test_metrics_exporter.py | - | fake_start | (port) | Needs Documentation |
| tests/utils/test_metrics_exporter.py | - | test_metrics_definitions | () | Needs Documentation |
| tests/utils/test_metrics_exporter.py | - | test_metrics_server_start | (monkeypatch) | Needs Documentation |
| tests/utils/test_metrics_exporter.py | - | test_record_metrics | () | Needs Documentation |
| tests/utils/test_metrics_exporter.py | - | test_start_metrics_server_custom_port | (prometheus_multiproc_fixture) | Needs Documentation |
| tests/utils/test_metrics_exporter.py | - | test_start_metrics_server_default_port | (mock_start_http_server) | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | mock_bind | (addr) | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | mock_bind | (addr) | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | mock_bind | (addr) | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | test_check_ports_available_conflicts | (mocker) | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | test_check_ports_available_range_violation | () | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | test_check_ports_available_success | (mocker) | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | test_skip_lmstudio_port | (mocker) | Needs Documentation |
| tests/utils/test_port_conflict_checker.py | - | test_validate_port_range | () | Needs Documentation |
| ui/app.py | - | get_agent | (agent_name) | Needs Documentation |
| ui/app.py | - | list_agents | () | Needs Documentation |
| ui/app.py | - | status | () | Needs Documentation |
