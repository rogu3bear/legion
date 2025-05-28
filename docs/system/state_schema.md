<!-- File: docs/system/state_schema.md -->

# State Repository Schema

The persistent state repository stores two primary tables in `memory/state/repo.json`.

| Table    | Fields                                   |
|----------|------------------------------------------|
| `agents` | `id`, `role`, `capabilities`, `token`, `tasks[]` |
| `tasks`  | `id`, `agent`, `directive`, `payload`, `priority`, `state` |

The `queue` section maintains an ordered list of pending tasks referencing entries in `tasks`.

---

## SQL Table Schema (Optional)

Tasks managed by the orchestrator are stored in an in-memory repository backed
by an optional SQL table (`task_registry`). Each record follows this schema:

| Field  | Type   | Description                     |
|------- |--------|---------------------------------|
| id     | str    | UUID for the task               |
| tags   | list   | Arbitrary tagging information   |
| owner  | str    | Requesting user or system       |
| agent  | str    | Assigned agent (optional)       |
| status | str    | Task status enum                |

The Alembic migration `20240520_add_task_registry_table.py` creates the
persistent table with the same columns.

### Persistence Options

Set `LEGION_STATE_BACKEND=sqlite` to store tasks in
`$LEGION_DATA_DIR/state/legion.db` instead of memory. Run
`python legion/orchestrator/state_repo.py --migrate` to initialise the
database.
