# State Repository Schema

The persistent state repository stores two primary tables in `memory/state/repo.json`.

| Table    | Fields                                   |
|----------|------------------------------------------|
| `agents` | `id`, `role`, `capabilities`, `token`, `tasks[]` |
| `tasks`  | `id`, `agent`, `directive`, `payload`, `priority`, `state` |

The `queue` section maintains an ordered list of pending tasks referencing entries in `tasks`.
