# Legion Framework

A modular, persona-driven agent framework for personal automation with a Discord social-feed UX.

## Features

- Multiple specialized AI agents working together
- Discord integration for real-time updates and interaction
- Extensible architecture for adding new agents and capabilities

## Setup

1. Create a .env folder with your `.env` file containing the needed keys.
2. Install dependencies: `pip install -r requirements.txt`
3. **Initialize agent memory:** `python scripts/init_memory.py`
   - _Run this script after installing dependencies and whenever you add new agents._
4. Run the bot as usual: `./scripts/start_bot.sh`

## Discord Setup

Each agent in `agent-definitions/*.yaml` must specify a `discord_channel_id` field, which is the numeric Discord channel ID where the agent will post and receive messages. Example:

```yaml
# Example agent YAML
name: architect_agent
... # other fields
# Discord channel for this agent
# Required: numeric channel ID (right-click channel > Copy ID in Discord)
discord_channel_id: 123456789012345678
```

**Adding or Updating Agent Channels:**
- To add a new agent, create a YAML in `agent-definitions/` and assign a unique `discord_channel_id`.
- To update a channel, change the `discord_channel_id` in the YAML.

**Required Bot Permissions:**
- The bot must have the following permissions in each agent channel:
  - CONNECT
  - SEND_MESSAGES
  - EMBED_LINKS
- If any permission is missing, startup will fail and `/status` will report an error.

## Project Structure

- `src/` - Core framework code
  - `ux_feed.py` - Discord feed renderer
  - `agent-definitions/` - Agent persona YAML definitions
  - `tools/` - Shared tools and utilities
- `config/` - Configuration files
- `scripts/` - Utility scripts
  - `init_memory.py` - Initializes per-agent memory directories and files for all agents defined in `agent-definitions/`.
- `memory/` - Persistent, versioned storage for each agent

## Agents

1. **Architect Agent**
   - System architecture and design decisions
   - Code review and best practices
   - Technical planning

2. **Therapist Agent**
   - Emotional support and guidance
   - Active listening and validation
   - Constructive feedback

3. **Metrics Agent**
   - Performance tracking and analysis
   - Data visualization
   - Trend identification

4. **UX Designer Agent**
   - User experience improvements
   - Interface design
   - Accessibility considerations

## Web UI

A simple web interface is available for viewing the Legion event feed in real time.

### Launching the Web UI

1. Ensure your Python virtual environment is set up and dependencies are installed:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r interface/requirements.txt
   ```
2. Start the web server:
   ```bash
   ./scripts/launch_ui.sh
   ```
3. Open your browser to [http://localhost:8000](http://localhost:8000) to view the feed.

The UI will display the latest Legion events and update live via WebSocket if supported by your browser.

## Discord Commands

- `/list_agents` — show available personas
- `/ask <agent> <prompt>` — query a single agent
- `/broadcast <prompt>` — run all agents on the prompt

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
