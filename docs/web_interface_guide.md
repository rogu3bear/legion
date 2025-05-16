# Legion Web Interface Guide

This guide provides comprehensive instructions for using the Legion Web Interface to manage agents, tasks, and monitor the system.

## 1. Overview

The Legion Web Interface provides a modern, feature-rich control plane for:
- Agent lifecycle management
- Task creation and monitoring
- System metrics and logging
- Memory system exploration
- Real-time updates via WebSocket

## 2. Access & Authentication

### Endpoints
- Web UI: `http://<your-host>:8000`
- API Documentation: `/docs` (Swagger UI) or `/redoc` (ReDoc)
- WebSocket: `ws://<your-host>:8000/ws`

### Authentication
1. **Login**: Use the `/auth/login` endpoint with your credentials
2. **JWT Tokens**: Store the returned access token for API requests
3. **Token Refresh**: Use `/auth/refresh` to obtain new access tokens
4. **Permissions**: Actions are controlled by role-based access (Admin, AgentOperator, User)

## 3. Dashboard

The main dashboard (`/`) provides:
- System status overview
- Active agents count
- Running tasks
- Memory system statistics
- Quick navigation cards

### Navigation Cards
- **Agent Management**: Control and monitor agents
- **Task Management**: Create and track tasks
- **Memory Explorer**: Search and browse stored knowledge
- **System Metrics**: View performance data
- **Logs**: Access system logs

## 4. Agent Management

### Agent List View
- Lists all registered agents
- Shows current status (running/stopped/error)
- Displays basic metrics (messages handled, tasks completed)
- Quick action buttons (start/stop/restart)

### Agent Details
- **Status**: Detailed operational status
- **Configuration**: View and edit settings
- **Metrics**: Performance data
- **Logs**: Agent-specific logs
- **Memory**: Access agent's memory store

### Agent Controls (Admin/AgentOperator)
- **Start**: Launch an agent
- **Stop**: Gracefully stop an agent
- **Restart**: Stop and restart an agent
- **Reload Config**: Update agent settings
- **Trigger Assessment**: Run agent self-assessment

## 5. Task Management

### Task Creation
1. Select target agent
2. Define task parameters
3. Set priority (optional)
4. Submit task

### Task List
- View all tasks with status
- Filter by agent/status
- Sort by various criteria
- Real-time updates via WebSocket

### Task Details
- Current status
- Execution progress
- Related logs
- Output/results
- Error information (if any)

### Task Controls
- Cancel running tasks
- Retry failed tasks
- Archive completed tasks

## 6. Memory System

### Search
- Full-text search across all memories
- Agent-specific memory search
- Semantic similarity search
- Filter by date/type

### Document Management
- List stored documents
- View document versions
- Download documents
- Search within documents

## 7. Real-Time Updates

### WebSocket Endpoints
- `/ws/events`: System-wide events
- `/ws/agents/{agent_name}/feed`: Agent-specific updates
- `/ws/system/metrics`: Performance metrics

### Event Types
- Agent status changes
- Task updates
- System metrics
- Error notifications
- Memory operations

## 8. System Settings

### Configuration
- System-wide settings
- Agent defaults
- Memory system parameters
- Logging levels

### User Management (Admin)
- Create/modify users
- Assign roles
- Manage permissions
- View audit logs

## 9. Troubleshooting

### Common Issues
1. **Connection Problems**
   - Check orchestrator status
   - Verify WebSocket connection
   - Validate authentication token

2. **Permission Errors**
   - Confirm user role
   - Check token expiration
   - Review audit logs

3. **Performance Issues**
   - Monitor system metrics
   - Check resource usage
   - Review task queue

### Support Resources
- System logs
- Error messages
- Performance metrics
- Documentation links

## 10. Best Practices

1. **Agent Management**
   - Monitor agent health regularly
   - Review logs for errors
   - Update configurations carefully
   - Test changes in staging

2. **Task Management**
   - Set appropriate priorities
   - Monitor long-running tasks
   - Clean up completed tasks
   - Document task patterns

3. **Memory Management**
   - Regular cleanup of old data
   - Monitor storage usage
   - Optimize search patterns
   - Back up important data

4. **Security**
   - Regular password updates
   - Token management
   - Access review
   - Audit log monitoring
