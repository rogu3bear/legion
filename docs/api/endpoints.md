# API Endpoints

| Method | Path | Auth | Response |
| ------ | ---- | ---- | -------- |
| GET | /api/v1/agents | Token | JSON list |
| POST | /api/v1/tasks | Token | Task ID |
| GET | /api/v1/metrics | None | Prometheus |
| POST | /api/v1/agent/register | None | Token string |
| GET | /api/v1/agent/{id}/status | None | Agent JSON |

*This list is incomplete. TODO: auto-generate from OpenAPI schema.*
