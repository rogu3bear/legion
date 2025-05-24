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

# Discord Integration Enhancement

## Overview

Enhanced Discord integration for the Legion agent system, providing improved message formatting, better error handling, and seamless agent-to-Discord communication.

## Key Components

### Discord Bridge (`legion/utils/discord_bridge.py`)

A centralized utility module providing:

- **DiscordBridge Class**: Core Discord communication functionality
- **MessageType Enum**: Standardized message categorization (INFO, SUCCESS, WARNING, ERROR)
- **Standalone Functions**: Easy-to-use convenience methods
- **Orchestrator Integration**: Callback system for agent message routing

### Enhanced BaseAgent (`legion/agents/base.py`)

Updated agent base class with:

- **Smart Message Type Detection**: Automatically categorizes messages based on content
- **Channel Routing**: Flexible channel ID resolution with multiple fallback strategies
- **Rich Formatting**: Embedded messages with fields for structured data
- **Error Resilience**: Graceful fallback to original messaging system
- **New Methods**:
  - `send_status_update()`: Formatted status notifications
  - `send_error_notification()`: Error alerts with context
  - `send_success_notification()`: Success messages with metrics

## Channel Configuration

### Environment Variables

```bash
# Core Discord Configuration
DISCORD_TOKEN=your_bot_token_here
AGENT_FEED_CHANNEL_ID=1375645390178615408

# Agent-specific Channel IDs (optional)
DOCTOR_CHANNEL_ID=channel_id
RESEARCHER_CHANNEL_ID=channel_id
METRICS_CHANNEL_ID=channel_id
```

### Channel Routing Logic

1. **Agent-specific channel**: `{AGENT_NAME}_CHANNEL_ID` environment variable
2. **Orchestrator mapping**: Agent channel IDs from orchestrator configuration
3. **Default fallback**: `AGENT_FEED_CHANNEL_ID` for all agent messages

## Usage Examples

### Basic Agent Integration

```python
# In any agent class inheriting from BaseAgent

# Simple status update
await self.send_status_update("Task completed", {
    "Files Processed": 42,
    "Errors": 0,
    "Duration": "5m 23s"
})

# Error notification with context
await self.send_error_notification(
    "API connection failed",
    context="External service timeout"
)

# Success notification with metrics
await self.send_success_notification("Analysis completed", {
    "Accuracy": "98.5%",
    "Records": 1205,
    "Time": "3m 12s"
})
```

### Direct Discord Bridge Usage

```python
from legion.utils.discord_bridge import send_discord_embed, MessageType

# Send formatted embed message
await send_discord_embed(
    "SystemAlert",
    "High memory usage detected",
    MessageType.WARNING,
    fields=[
        ("Memory Usage", "89%"),
        ("Threshold", "85%"),
        ("Action", "Cleanup initiated")
    ]
)
```

### Orchestrator Integration

```python
from legion.utils.discord_bridge import create_orchestrator_callback

# Create callback for orchestrator
callback = create_orchestrator_callback()

# Use in orchestrator's _post_agent_message method
await callback(agent_name, message)
```

## Message Types & Formatting

### MessageType.INFO (Blue)
- General information and status updates
- Default color: Blue (#3498db)
- Icon: ℹ️

### MessageType.SUCCESS (Green)
- Successful operations and completions
- Default color: Green (#2ecc71)
- Icon: ✅

### MessageType.WARNING (Orange)
- Warnings and cautions
- Default color: Orange (#f39c12)
- Icon: ⚠️

### MessageType.ERROR (Red)
- Errors and failures
- Default color: Red (#e74c3c)
- Icon: ❌

## Testing

### Integration Test Script

Run `scripts/test_discord_integration.py` to verify:

- Basic message sending functionality
- All message type formatting
- Agent behavior simulation
- Orchestrator integration

### Verification Commands

```bash
# Test Discord bridge imports
python -c "from legion.utils.discord_bridge import DiscordBridge; print('✅ Success')"

# Test updated BaseAgent
python -c "from legion.agents.base import BaseAgent; print('✅ Success')"

# Run full integration test
python scripts/test_discord_integration.py
```

## Migration Notes

### Backward Compatibility

- Existing `post_to_discord()` method preserved with enhanced functionality
- Fallback to original implementation if new bridge fails
- No breaking changes to existing agent code

### Gradual Adoption

Agents can gradually adopt new methods:
1. Continue using `post_to_discord()` for basic messages
2. Add `send_status_update()` for structured updates
3. Use `send_error_notification()` and `send_success_notification()` for specific scenarios

## Error Handling

### Graceful Degradation

- New bridge failure → Fallback to original method
- Missing channel ID → Log error, attempt default channel
- Discord API errors → Log and continue execution
- Import errors → Graceful fallback without system failure

### Debugging

- Comprehensive logging at all failure points
- Clear error messages with context
- Fallback behavior notifications
- Import error handling for circular dependency prevention

## Future Enhancements

### Planned Features

- **Rate Limiting**: Automatic message throttling
- **Message Queuing**: Batch processing for high-volume scenarios
- **Rich Media**: Image and file attachment support
- **Interactive Elements**: Buttons and dropdowns for Discord interactions
- **Analytics**: Message delivery tracking and metrics

### Configuration Expansion

- Per-agent message type customization
- Channel-specific formatting rules
- Timezone-aware timestamps
- Message retention policies

## Troubleshooting

### Common Issues

1. **Messages not sending**: Check `DISCORD_TOKEN` and channel IDs
2. **Import errors**: Verify Python path and module structure
3. **Formatting issues**: Ensure fields are properly formatted as tuples
4. **Rate limiting**: Add delays between bulk message operations

### Debug Mode

Enable debug logging for detailed Discord integration information:

```python
import logging
logging.getLogger("legion.utils.discord_bridge").setLevel(logging.DEBUG)
```
