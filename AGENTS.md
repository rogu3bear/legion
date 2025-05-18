# Legion Agents Directory

A central reference for every agent active in the **Legion** ecosystem: roles, capabilities, endpoints, and health-check details.
_Last updated: **May 17 2025**_

---
## Legend
| Emoji | Meaning |
|-------|---------|
| 🔑 | Core / mission-critical |
| 🛠️ | Development utility |
| 📊 | Metrics & logging |
| 💬 | Communication / UX |
| 🩺 | Health & observability |

---
## Orchestrator 🔑
* **Role**  Central brain; delegates tasks, routes messages, enforces policy.
* **Port Map**  PUB `7808` | SUB `7809` | REST `7803` | Interface API `7804` | Middleware `7805` | Researcher API `7807` | Redis `7810`
* **Key Capabilities**
  `dispatch_task` • `cancel_task` • `sync_state` • `rebalance_load`
* **Heartbeat Expectation**  < 5 s.
* **Endpoints**
  `POST /api/v1/tasks` • `PATCH /api/v1/tasks/{id}`

---
## Worker Agents

### Architect 🔑
* **Role**  Generates high-level blueprints & multi-step plans.
* **Capabilities**  `create_plan` • `validate_module` • `diagram_system`
* **LLM Usage**: Utilizes model `meta-llama-3.1-8b-instruct` via the system's LLM client (e.g., for LMStudio). Config: `legion/configs/agents.yaml`.
* **Default Owner Tags**  `design`, `system`
* **Status Topics**  `architect.status`

### Therapist 🔑
* **Role**  Gate-keeps all agent function calls; enforces logic & ethics.
* **Capabilities**  `validate_intent` • `sanitize_prompt` • `reroute`
* **LLM Usage**: Utilizes model `meta-llama-3.1-8b-instruct` via the system's LLM client. Config: `legion/configs/agents.yaml`.
* **Tags**  `compliance`, `guard`

### Metrics 📊
* **Role**  Collects runtime metrics, pushes to Prometheus or Influx.
* **Capabilities**  `record_counter` • `record_histogram` • `push_metric`
* **LLM Usage**: Utilizes model `meta-llama-3.1-8b-instruct` via the system's LLM client. Config: `legion/configs/agents.yaml`.
* **Exports**  `/metrics` on port `7806`

### UX Designer 💬
* **Role**  Improves prompts, copy, and UI micro-interactions.
* **Capabilities**  `rewrite_text` • `suggest_layout`
* **LLM Usage**: Utilizes model `meta-llama-3.1-8b-instruct` via the system's LLM client. Config: `legion/configs/agents.yaml`.

### Ping 🛠️
* **Role**  Simple liveness echo; measures round-trip latency.
* **Capabilities**  `ping` • `sleep`
* **LLM Usage**: Utilizes model `meta-llama-3.1-8b-instruct` via the system's LLM client. Config: `legion/configs/agents.yaml`.

### Echo 🛠️
* **Role**  Verbose logger; mirrors commands for audit & training data.
* **Capabilities**  `echo_task` • `log_payload`
* **LLM Usage**: Utilizes model `meta-llama-3.1-8b-instruct` via the system's LLM client. Config: `legion/configs/agents.yaml`.
* **Note**  High output volume— route to `agent-feed` channel.

### Healthcheck 🩺
* **Role**  Active monitoring of CPU, RAM, and container health.
* **Capabilities**  `collect_health` • `report_anomaly`
* **LLM Usage**: Utilizes model `meta-llama-3.1-8b-instruct` via the system's LLM client. Config: `legion/configs/agents.yaml`.
* **Endpoints**  `GET /api/v1/agents/health`

### Developer 🛠️
* **Role**  Go-based Developer agent for code review, refactoring, and debugging.
* **Capabilities**  `code_review` • `refactor` • `debug`
* **LLM Usage**: LLM model not explicitly specified in configuration (`legion/configs/developer.yaml`). Task execution may or may not involve direct LLM calls.
* **Config**: `legion/configs/developer.yaml`

---
## Capability → Agent Map (excerpt)
| Capability            | Primary Agent(s) |
|-----------------------|------------------|
| `create_plan`         | Architect        |
| `validate_intent`     | Therapist        |
| `record_counter`      | Metrics          |
| `rewrite_text`        | UX Designer      |
| `ping`                | Ping             |
| `echo_task`           | Echo             |
| `collect_health`      | Healthcheck      |
| `code_review`         | Developer        |
| `refactor`            | Developer        |
| `debug`               | Developer        |

_For a live list use `GET /api/v1/agents/capabilities`._

---
## Heartbeat & SLA
| Agent         | Status Window | Offline Threshold | Escalate To              |
|---------------|---------------|-------------------|--------------------------|
| Orchestrator  | 5 s           | 10 s              | PagerDuty #P0            |
| Architect     | 15 s          | 30 s              | Orchestrator auto-restart |
| Metrics       | 30 s          | 60 s              | Healthcheck agent        |

---
## Development Notes
* **Adding a new agent**
  1. Reserve host port in `.env.ports.example`.
  2. Implement heartbeat ping.
  3. Update `legion/orchestrator/routing_map.py`.
  4. Append entry here.
* **LLM Interaction**: Agents configured with an `llm_model` typically interact with Large Language Models through a centralized client interface within the system (e.g., `ILLMClient`). This client is responsible for connecting to the configured LLM service, such as LMStudio.
* **Tag Rules**  All persistent tasks must include at least one **project** tag (`[Legion | Development]`, `[Business | AuchShop]`, etc.) plus functional tags.

---
© 2025 AuchIndustries — internal use only.
