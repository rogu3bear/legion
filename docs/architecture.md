# Legion Architecture

This document provides a high-level overview of Legion's modules, data flows, and design rationale.

## Modules
- Orchestrator
- Agents
- Skills
- Memory
- Integration
- Interface 

## Unified Agent Message Handling

All agents in Legion now use a single, unified message handling pipeline inherited from BaseAgent. This pipeline:
- Loads the agent's default prompt from config (with fallback)
- Retrieves top-K relevant memory snippets using the memory module's index helper
- Fetches the last N messages from the Discord thread
- Builds the LLM payload in the order: system prompt, memory summary, thread history, user message
- Sends the payload to the LLM and posts the reply
- Extracts and stores new memory items from the reply

This eliminates all per-agent prompt orchestration and ensures robust, consistent behavior across all personas.

## Message Dispatch Flow (Mermaid)

```mermaid
flowchart TD
    subgraph Discord Integration
        A[on_message(event)]
        A -->|wraps event| B[context dict]
    end
    B -->|calls| C[orchestrator.dispatch_message(agent_name, context)]
    C -->|calls| D[agent.handle_message(context)]
    D -->|returns| E[response]
```

**Method signatures:**
- `orchestrator.dispatch_message(agent_name: str, context: dict)`
- `agent.handle_message(context: dict)` 