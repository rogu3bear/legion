# EchoAgent

**Role:** Logging helper that persists events to the database.

## Methods

- `log(event)` - Persist the event and return its UUID.
- `record(event)` - Record an EchoEvent to Redis with secondary indexes.
