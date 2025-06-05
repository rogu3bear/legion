# ResearcherAgent

**Role:** Agent that conducts research and synthesizes findings.

## Methods

- `setup(orchestrator)` - Prepare utilities and register with orchestrator.
- `conduct_research(query, sources)` - Search the web and return raw data, using Redis cache when available.
- `synthesize_findings(raw_data)` - Synthesize raw search data into a report.
- `process_message(msg, ctx)` - Dispatch message to research or synthesis handlers.
