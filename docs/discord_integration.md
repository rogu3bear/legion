# Discord Integration

## Overview

The Legion Discord integration provides a robust interface between the agent system and Discord, enabling real-time communication, command execution, and system monitoring. This document outlines the architecture, components, and usage of the Discord integration.

## Architecture

### Components

1. **Bot Core** (`integration/discord/bot.py`)
   - Main Discord bot instance
   - Message routing and event handling
   - Thread and channel management

2. **Command Handler** (`legion/discord/commands.py`)
   - Command registration and processing
   - Implementation of core commands
   - Error handling and logging

3. **Cogs**
   - **Orchestrator** (`cogs/orchestrator.py`): Agent management and system control
   - **Health** (`cogs/health.py`): System monitoring and diagnostics
   - **UX Feed** (`cogs/ux_feed.py`): User experience updates and notifications

4. **Agent Integration**
   - Message posting and thread management
   - Error handling and notifications
   - State synchronization

## Command Reference

### Agent Management

#### Configuration
```
/config_agent <agent> <model> <temperature> <max_tokens>
```
Configure agent settings including model, temperature, and token limits.

#### Interaction
```
/ask <agent> <question>
```
Send a question to a specific agent.

#### Assessment
```
/assess [agent]
```
Trigger agent self-assessment (optional agent parameter).

### System Control

#### Configuration Reload
```
/reload_configs
```
Reload all agent configurations from disk.

#### Broadcast
```
/broadcast <message>
```
Send message to all agents simultaneously.

#### Status
```
/status
```
Get current system status and metrics.

### Health Monitoring

#### Health Check
```
/healthcheck
```
Run comprehensive system health check.

#### Latency
```
/ping
```
Check bot and system latency.

#### Uptime
```
/uptime
```
Display system uptime statistics.

### User Experience

#### Feed Subscription
```
/ux_subscribe
/ux_unsubscribe
```
Manage UX feed subscriptions.

## Message Flow

### Incoming Messages
1. Discord message received
2. `on_message` event handler triggered
3. Message routed to appropriate agent
4. Agent processes message
5. Response posted to Discord

### Command Processing
1. User enters command
2. Command handler validates input
3. Implementation function executed
4. Results posted to Discord
5. Logs updated

### Error Handling
1. Error detected
2. Error logged to system
3. User notified via Discord
4. Error details stored for analysis
5. Recovery procedures initiated if needed

## Thread Management

### Thread Creation
- Automatic thread creation for new conversations
- Thread naming based on context
- Thread archival after inactivity

### Thread History
- Message history retrieval
- Context preservation
- Memory integration

## Security

### Authentication
- Bot token management
- Command permission levels
- User role verification

### Rate Limiting
- Message rate limiting
- Command cooldowns
- API quota management

## Best Practices

### Message Formatting
1. Use code blocks for code snippets
2. Implement embeds for structured data
3. Split long messages appropriately
4. Include relevant context

### Error Handling
1. Provide clear error messages
2. Log errors comprehensively
3. Implement graceful fallbacks
4. Maintain system stability

### Performance
1. Optimize message processing
2. Implement caching where appropriate
3. Monitor resource usage
4. Scale based on demand

## Troubleshooting

### Common Issues

1. **Message Not Delivered**
   - Check bot permissions
   - Verify channel access
   - Confirm rate limits

2. **Command Failures**
   - Validate command syntax
   - Check user permissions
   - Review error logs

3. **Performance Issues**
   - Monitor message queue
   - Check system resources
   - Review rate limits

## Development

### Adding New Commands

1. Create command implementation
2. Register with command handler
3. Add error handling
4. Update documentation
5. Test thoroughly

### Extending Functionality

1. Identify extension point
2. Implement new feature
3. Add necessary commands
4. Update documentation
5. Test integration

## Configuration

### Environment Variables
```
DISCORD_TOKEN=<bot_token>
DISCORD_CHANNELS_PATH=legion/configs/channels.txt
```

### Bot Settings
```yaml
discord:
  command_prefix: "/"
  activity_type: "playing"
  activity_name: "with agents"
  status: "online"
```

## Monitoring

### Metrics
- Message processing time
- Command success rate
- Error frequency
- Resource usage

### Alerts
- System status changes
- Error thresholds
- Performance degradation
- Security events

## Future Enhancements

1. **Advanced Threading**
   - Improved context management
   - Better history integration
   - Enhanced search capabilities

2. **Command Expansion**
   - More agent interactions
   - Advanced system control
   - Enhanced monitoring

3. **Performance Optimization**
   - Message batching
   - Caching improvements
   - Resource optimization

4. **Security Enhancements**
   - Advanced authentication
   - Better rate limiting
   - Improved logging
