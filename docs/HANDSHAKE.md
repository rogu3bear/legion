# Agent Registration Handshake

This document outlines the multi-phase registration sequence between a worker agent and the orchestrator.

| Phase | Direction | Payload |
|-------|-----------|---------|
| `INITIAL_REQUEST` | Agent → Orchestrator | `{agent_id, capabilities}` |
| `AUTH_CHALLENGE` | Orchestrator → Agent | `{challenge_token, nonce}` |
| `AUTH_RESPONSE` | Agent → Orchestrator | `{agent_id, signed_challenge}` |
| `FINAL_ACK` | Orchestrator → Agent | `{status:"registered", session_id, ts}` |

All phases are logged to the Redis list `handshake_log` and agent state keys `agent:<id>:state` are updated accordingly.
