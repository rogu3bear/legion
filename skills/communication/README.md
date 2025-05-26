# Communication Skills

<!-- reviewme: This directory is currently empty - contains only placeholder documentation -->

**Status**: Placeholder directory - no implementations yet

This directory is reserved for future communication skills including:

- Discord integration utilities
- Message formatting helpers
- Notification management

## Current Implementation

The actual communication functionality is currently implemented in:
- `integration/discord/` - Discord bot integration
- `integration/discord/cogs/` - Discord command handlers
- `interface/websocket_manager.py` - WebSocket communication
- `interface/api/v1/endpoints/` - REST API endpoints

## Future Plans

This directory may be populated with reusable communication utilities that can be shared across agents and interfaces.

## Skills

- `discord_utils.py` - Discord helpers (planned)
- `message_format.py` - Message formatting (planned)
- `notification.py` - Alert management (planned)

## Usage

```python
from skills.communication import discord_utils, message_format
```

*Part of Legion Re-org Safety Blueprint - Phase 2*
