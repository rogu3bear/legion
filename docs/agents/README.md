# Agent Behaviours
| Agent | Role | Endpoint | Port |
|-------|------|----------|------|
| Orchestrator | Task routing | /queue | 7803 |
| Echo | Logging | /echo | 7804 |
*Details*: [../legacy/agents/]
=======

| Agent | Role | Key Capabilities |
|-------|------|-----------------|
| Architect | Generates blueprints and multi-step plans | `create_plan`, `validate_module` |
| Therapist | Validates intent and sanitizes prompts | `validate_intent`, `sanitize_prompt` |
| Metrics | Collects runtime metrics | `record_counter`, `push_metric` |
| UX Designer | Improves wording and layout suggestions | `rewrite_text`, `suggest_layout` |
| Ping | Measures liveness and latency | `ping`, `sleep` |
| Echo | Mirrors payloads for logging | `echo_task`, `log_payload` |
| Healthcheck | Reports container health | `collect_health`, `report_anomaly` |

👉 Deep dive: legacy/agents/*

