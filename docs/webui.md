# Legion WebUI

The Legion WebUI is a lightweight, intuitive web interface for managing Legion's MCP (Model Control Protocol) system. It provides a modern React-based interface for agent management, prompt editing, and direct communication with LM Studio.

## Features

### 🤖 Agent Selector
- **Dynamic Agent Loading**: Automatically fetches all available agents from the Legion system
- **Dropdown Interface**: Clean, searchable dropdown for agent selection
- **Real-time Updates**: Agents list updates dynamically as new agents are added

### ✏️ Prompt Editor
- **Markdown Support**: Full markdown editing capabilities for agent prompts
- **Live Preview**: Real-time editing with immediate visual feedback
- **Auto-save Feedback**: Clear confirmation messages when prompts are saved
- **Agent-specific Editing**: Load and edit prompts for any selected agent

### 💬 LM Studio Chat Interface
- **Direct Integration**: Seamless connection to LM Studio via proxy endpoints
- **Conversational UI**: Modern chat interface with message history
- **Real-time Responses**: Live communication with LM Studio models
- **Error Handling**: Graceful error handling for connection issues

## Access

The WebUI is available at: `http://localhost:8000/webui`

## API Endpoints

The WebUI uses the following demo endpoints (no authentication required):

- `GET /api/demo/agents` - List all available agents
- `GET /api/demo/prompts/{agent_name}` - Get specific agent prompt
- `PUT /api/demo/prompts/{agent_name}` - Update agent prompt
- `POST /api/v1/lmstudio/chat` - Chat with LM Studio

## Technical Details

### Frontend Stack
- **React 18**: Via CDN for minimal dependencies
- **Tailwind CSS**: For modern, responsive styling
- **Babel Standalone**: For JSX transformation in the browser

### Backend Integration
- **FastAPI**: RESTful API endpoints
- **File-based Storage**: Prompts stored as markdown files in `legion/prompts/`
- **LM Studio Proxy**: Direct proxy to LM Studio chat completions

### Security
- **Content Security Policy**: Configured to allow necessary CDN resources
- **Demo Mode**: Unauthenticated endpoints for rapid prototyping
- **Input Validation**: Server-side validation for all API requests

## Usage

1. **Navigate to WebUI**: Open `http://localhost:8000/webui` in your browser
2. **Select Agent**: Choose an agent from the dropdown to load its prompt
3. **Edit Prompt**: Modify the prompt content in the editor
4. **Save Changes**: Click "Save Prompt" to persist changes
5. **Chat with LM Studio**: Use the chat interface to test prompts and interact with models

## Development

The WebUI is designed for rapid iteration and minimal complexity:

- **Single File Template**: All React code contained in `interface/templates/webui.html`
- **No Build Process**: Direct browser execution with CDN dependencies
- **Hot Reload**: FastAPI's reload functionality for backend changes

## Future Enhancements

- Authentication integration for production use
- Advanced prompt templating features
- Agent performance metrics integration
- Multi-model support beyond LM Studio
- Collaborative editing capabilities
