# ASCII Diagrams

This page provides plain ASCII diagrams illustrating key function pipelines in Legion.

## Dispatch Overview
```
User -> Interface -> Orchestrator -> Agent -> Memory -> LLM
      <-                         <-         <-
```

## Agent Processing Steps
```
+---------------+
| BaseAgent     |
+---------------+
| validate      |
| mem_retrieve  |
| build_prompt  |
| call_llm      |
| mem_store     |
| respond       |
+---------------+
```

These diagrams summarize how messages flow through the system at a glance.
