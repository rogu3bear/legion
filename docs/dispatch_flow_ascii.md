# Legion Dispatch Flow (ASCII)

## Message Pipeline
```
User (Discord)
   |
   v
DiscordAdapter
   |
   v
Middleware
   |
   v
Orchestrator
   |
   v
TherapistAgent
   |
   v
Specific Agent
   |
   v
Orchestrator
   |
   v
DiscordAdapter
```

## Agent Processing Steps
```
+-------------+
| BaseAgent   |
+-------------+
      |
      v
validate_payload
      |
      v
retrieve_memories
      |
      v
perform_task
      |
      v
store_memories
      |
      v
build_response
```
