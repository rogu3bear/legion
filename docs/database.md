# Database Models

This overview summarizes the primary models stored in `memory/db/legion.db`.
The database is managed via SQLAlchemy and Alembic migrations.

## Conversation
Tracks chat threads started through the web interface.

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | integer | Primary key |
| `thread_id` | string | Unique conversation identifier |
| `agent_id` | integer | References `agents.id` |
| `title` | string | Optional title |
| `created_at` | datetime | Timestamp of creation |

## Directive
Defines policy directives for individual agents.

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | integer | Primary key |
| `agent_id` | integer | References `agents.id` |
| `content` | text | Directive text |
| `is_active` | boolean | Enabled flag |
| `created_at` | datetime | Timestamp of creation |
