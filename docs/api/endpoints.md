# API Endpoints Cheat-Sheet

This table is generated from `openapi.json`.

```python
import json, pathlib
schema = json.loads(pathlib.Path('openapi.json').read_text())
print("| Method | Path | Auth | Summary | Response |")
print("|-------|------|------|--------|---------|")
for path, methods in schema.get('paths', {}).items():
    for method, meta in methods.items():
        auth = 'Yes' if meta.get('security') else 'No'
        summary = meta.get('summary', '')
        resp = ', '.join(meta.get('responses', {}).keys())
        print(f"| {method.upper()} | {path} | {auth} | {summary} | {resp} |")
```
| Method | Path | Auth | Summary | Response |
|-------|------|------|--------|---------|
| POST | /api/v1/auth/login | No | Login for Access Token | 200, 422 |
| GET | /api/v1/auth/me | Yes | Get Current User | 200 |
| POST | /api/v1/auth/register | No | Register New User | 201, 422 |
| POST | /api/v1/auth/logout | Yes | Logout User | 200 |
| GET | /api/v1/auth/me/preferences | Yes | Get User Preferences | 200 |
| PUT | /api/v1/auth/me/preferences | Yes | Update User Preferences | 200, 422 |
| POST | /api/v1/login/access-token | No | Obtain Access Token | 200, 422 |
| GET | /api/v1/agents/ | Yes | List All Agents | 200 |
| POST | /api/v1/agents/ | Yes | Create Agent | 201, 422 |
| GET | /api/v1/agents/{agent_id} | Yes | Get Agent by ID | 200, 422 |
| PUT | /api/v1/agents/{agent_id} | Yes | Update Agent | 200, 422 |
| DELETE | /api/v1/agents/{agent_id} | Yes | Delete Agent | 200, 422 |
| POST | /api/v1/agents/register | No | Register Agent | 200, 422 |
| GET | /api/v1/agents/{agent_name} | Yes | Get Agent Status | 200, 422 |
| GET | /api/v1/agents/{agent_name}/config | Yes | Get Agent Configuration | 200, 422 |
| PUT | /api/v1/agents/{agent_name}/config | Yes | Update Agent Configuration | 200, 422 |
| POST | /api/v1/agents/{agent_name}/dispatch | Yes | Dispatch Message to Agent | 200, 422 |
| POST | /api/v1/agents/{agent_name}/assess | Yes | Trigger Agent Self-Assessment | 200, 422 |
| POST | /api/v1/agents/{agent_name}/start | Yes | Start Agent | 200, 422 |
| POST | /api/v1/agents/{agent_name}/stop | Yes | Stop Agent | 200, 422 |
| POST | /api/v1/agents/{agent_name}/restart | Yes | Restart Agent | 200, 422 |
| POST | /api/v1/agents/reload | Yes | Reload All Agent Configurations | 200 |
| GET | /api/v1/agents/capabilities | Yes | List Agent Capabilities | 200 |
| GET | /api/v1/system/status | Yes | Get System Status | 200 |
| GET | /api/v1/system/metrics | Yes | Get System Metrics | 200 |
| GET | /api/v1/system/logs | Yes | Get System Logs | 200 |
| GET | /api/v1/system/memory/stats | Yes | Get Memory Statistics | 200 |
| GET | /api/v1/tasks/ | Yes | List Tasks | 200, 422 |
| POST | /api/v1/tasks/ | Yes | Submit New Task | 201, 422 |
| GET | /api/v1/tasks/{task_id} | Yes | Get Task Details | 200, 422 |
| DELETE | /api/v1/tasks/{task_id} | Yes | Cancel Task | 204, 422 |
| GET | /api/v1/registry/tasks/ | No | List Tasks | 200, 422 |
| POST | /api/v1/registry/tasks/ | No | Create Task | 201, 422 |
| GET | /api/v1/registry/tasks/{task_id} | No | Get Task | 200, 422 |
| DELETE | /api/v1/registry/tasks/{task_id} | No | Delete Task | 204, 422 |
| PATCH | /api/v1/registry/tasks/{task_id} | No | Update Task | 200, 422 |
| GET | /api/v1/queue/summary | No | Get Queue Summary | 200 |
| GET | /api/v1/agent/{agent_id}/tasks | No | Get Agent Tasks | 200, 422 |
| GET | /api/v1/memory/documents | Yes | List Memory Documents | 200 |
| GET | /api/v1/memory/documents/{doc_name} | Yes | Get Memory Document | 200, 422 |
| GET | /api/v1/memory/agents/{agent_name}/search | Yes | Search Agent Memory | 200, 422 |
| GET | /api/v1/memory/search | Yes | Search Global Memory | 200, 422 |
| POST | /api/v1/lmstudio/echo | No | Proxy payload to LM Studio completion endpoint | 200 |
| POST | /api/v1/echo/ | No | Send message to Echo agent | 200, 422 |
| GET | /api/v1/metrics/ | No | Prometheus metrics | 200 |
| GET | / | No | Read Root | 200 |
| GET | /api/feed | No | Get Feed | 200 |
| GET | /health | No | Health Check | 200 |
