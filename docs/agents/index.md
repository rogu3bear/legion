# Agents

Legion includes several specialized agents coordinated by the orchestrator.

| Agent | Role | Key Capabilities |
|-------|------|-----------------|
| Orchestrator | Central command | task dispatch, state sync |
| Architect | System planning | create_plan, validate_module |
| Therapist | Policy enforcement | validate_intent, sanitize_prompt |
| Metrics | Runtime metrics | record_counter, push_metric |
| UX Designer | Prompt tuning | rewrite_text, suggest_layout |
| Ping | Liveness checks | ping, sleep |
| Echo | Verbose logging | echo_task, log_payload |
| Healthcheck | Health monitoring | collect_health, report_anomaly |
| Developer | Code review (Go) | code_review, refactor |

Ports for these agents are defined in [architecture/ports.md](../architecture/ports.md).
