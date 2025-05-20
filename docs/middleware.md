# Middleware Overview

This document describes the consolidated middleware package located under
`legion/middleware` and `middleware/src/middleware`. The two directories now
share logic for directive validation, hallucination detection, and request
processing.

## Modules
- `validator.py` – validates directives against `legion/config/directives.yaml`.
- `hallucination_guard.py` – checks confidence scores to detect hallucinations.
- `middleware.py` – high-level request pipeline combining embedding validation
  and directive compliance.

## Logging
Middleware components emit structured logs via the standard Legion logging
setup. Significant events are also forwarded to the Echo agent using the helper
`legion.utils.agent_feed.post_agent_feed`.

## Current Issues
- Additional tests are needed to cover the new logging paths. *(TODO)*
- The FastAPI service under `middleware/src/main.py` still contains several TODO
  markers for context routing and authentication.
