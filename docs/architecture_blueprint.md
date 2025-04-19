# Architecture Blueprint

## High-Level System Diagram

```
[User/Discord] <-> [Discord Bot (src/discord_integration.py)] <-> [Orchestrator (src/orchestrator.py)]
    |                                                           |
    v                                                           v
[Agent Channels] <----------------------------------------> [Agents (agent-definitions/*.yaml)]
    |                                                           |
    v                                                           v
[Feed Renderer (src/ux_feed.py)] <-> [Web UI (interface/)]   [Agent Memory (memory/<agent>/)]
```

## Data Flow
- User interacts via Discord (slash commands, messages).
- Discord bot receives commands, routes to orchestrator.
- Orchestrator loads agent personas, manages registry, dispatches events.
- Each agent has persistent memory (logs, docs, key-value data).
- Agent actions and updates are posted to Discord channels as embeds (feed items).
- Web UI displays live feed of agent activity.
- All agent data is versioned and queryable for learning and self-assessment.
