# Refactor Log

## Unify Core Utilities
- Moved async Chroma client to `legion/core/utils/async_chroma_client.py`.
- Renamed sync implementation to `sync_chroma_client.py`.
- Added `README.md` explaining the difference.

## Deduplicate Network Helpers
- Removed duplicate `fetch_with_retries` from `legion/core/network.py`.
- Import canonical implementation from `legion/core/utils/network.py`.

## Unify Middleware Logic
- Relocated middleware modules into `legion/middleware/`.
- Consolidated hallucination guard into `HallucinationGuard` class.

## Centralize Discord Integration
- Created `integration/discord/utils.py` with `fetch_thread_history`.
- Updated `LegionBot` and `BaseAgent` to use shared utilities.

## Relocate HTTP Client
- Moved `http_client.py` to `legion/utils/` and added package init.

## Rename Placeholder Functions
- `placeholder_network` -> `basic_health_check`
- `search_placeholder` -> `vector_search`
- `summarize_placeholder` -> `summarize_snippets`
- `placeholder_indexing` -> `build_inverted_index`
