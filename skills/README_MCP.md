# Legion MCP Server

A comprehensive Model Context Protocol (MCP) server that provides LLM applications with seamless access to the Legion agent system, memory management, and AI-powered analysis capabilities.

## Overview

The Legion MCP Server integrates FastMCP with the Legion agent framework to provide:

- **Agent Memory Management**: Read/write agent memory, task logging, document storage
- **Vector Memory Search**: Store and search memories using embeddings
- **LLM Integration**: Support for LM Studio, OpenAI, and mock providers
- **Agent Diagnostics**: AI-powered agent analysis and troubleshooting
- **System Monitoring**: Real-time status and health checking
- **Resource Access**: MCP resources for agent data and system status
- **Interactive Prompts**: Pre-built prompts for common Legion operations

## Features

### 🔧 MCP Tools (14 total)

#### Memory Management
- `get_agent_memory` - Retrieve agent memory data
- `set_agent_memory` - Set agent memory values
- `log_agent_task` - Log tasks for agents
- `get_agent_task_log` - Retrieve agent task history
- `save_agent_document` - Save versioned documents
- `get_agent_document` - Retrieve agent documents
- `list_agent_documents` - List all agent documents

#### Vector Operations
- `store_vector_memories` - Store embeddings for similarity search
- `search_vector_memories` - Search memories by embedding similarity
- `perform_vector_search` - Search provided documents

#### AI-Powered Analysis
- `ask_llm` - Direct LLM interaction with configurable parameters
- `diagnose_agent_with_llm` - AI-powered agent diagnostics
- `analyze_agent_performance_with_llm` - Performance analysis using LLM
- `summarize_content` - Text summarization via LLM

#### System Operations
- `get_legion_system_status` - System status and health
- `get_llm_status` - LLM provider status
- `perform_web_search` - Web search functionality

### 📊 MCP Resources

- `memory://agents/{agent_name}/memory` - Agent memory data
- `memory://agents/{agent_name}/tasks` - Agent task logs
- `memory://agents/{agent_name}/documents` - Agent document list
- `legion://system/status` - System status information

### 💬 MCP Prompts

- `agent_diagnosis` - Agent troubleshooting template
- `agent_memory_analysis` - Memory pattern analysis template
- `system_health_check` - System health assessment template

## Quick Start

### 1. Installation

```bash
# Install FastMCP dependency
pip install "fastmcp>=2.3.0"

# The Legion MCP server is already integrated into your Legion installation
```

### 2. LLM Provider Setup

#### Option A: LM Studio (Recommended for Local Development)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model (e.g., Llama, Mistral, Codellama)
3. Start the local server (usually runs on `localhost:1234`)
4. Configure environment:

```bash
export LLM_PROVIDER=lm_studio
export LM_STUDIO_URL=http://localhost:1234/v1
export LM_STUDIO_API_KEY=not-needed  # Usually not required
```

#### Option B: OpenAI

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Configure environment:

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
export OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4
```

#### Option C: Mock Provider (Testing)

```bash
export LLM_PROVIDER=mock
```

### 3. Environment Configuration

Copy the example environment file:

```bash
cp .env.mcp.example .env.mcp
# Edit .env.mcp with your settings
```

### 4. Running the Server

#### As a Python Module

```bash
python -m skills.mcp_server --host localhost --port 8765
```

#### Directly

```bash
cd skills
python mcp_server.py --host localhost --port 8765
```

#### In-Memory (for development/testing)

```python
from skills.mcp_server import mcp
from fastmcp import Client

async with Client(mcp) as client:
    result = await client.call_tool("get_legion_system_status", {})
    print(result[0].text)
```

## Usage Examples

### Basic Agent Operations

```python
from fastmcp import Client
from skills.mcp_server import mcp

async with Client(mcp) as client:
    # Set agent memory
    await client.call_tool("set_agent_memory", {
        "agent_name": "my_agent",
        "key": "status",
        "value": "active"
    })
    
    # Log a task
    await client.call_tool("log_agent_task", {
        "agent_name": "my_agent",
        "task_data": {
            "action": "process_data",
            "status": "completed",
            "duration_ms": 1500
        }
    })
    
    # Get system status
    status = await client.call_tool("get_legion_system_status", {})
    print(status[0].text)
```

### AI-Powered Diagnostics

```python
# Diagnose agent issues using LLM
diagnosis = await client.call_tool("diagnose_agent_with_llm", {
    "agent_name": "problematic_agent",
    "symptoms": "High CPU usage, memory leaks, slow responses",
    "include_memory": True,
    "include_tasks": True
})

print(json.loads(diagnosis[0].text)["diagnosis"])
```

### Vector Memory Search

```python
# Store memories with embeddings
await client.call_tool("store_vector_memories", {
    "agent_name": "my_agent",
    "memory_snippets": [
        {
            "text": "Successfully processed user request",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
    ]
})

# Search similar memories
results = await client.call_tool("search_vector_memories", {
    "agent_name": "my_agent",
    "query_embedding": [0.15, 0.25, 0.35, 0.45, 0.55],
    "top_k": 3
})
```

### Direct LLM Interaction

```python
# Ask the LLM a question
response = await client.call_tool("ask_llm", {
    "prompt": "Explain the benefits of agent-based systems",
    "system_message": "You are an expert in distributed systems",
    "temperature": 0.3,
    "max_tokens": 500
})

print(json.loads(response[0].text)["response"])
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (lm_studio, openai, mock) | `mock` |
| `LM_STUDIO_URL` | LM Studio API endpoint | `http://localhost:1234/v1` |
| `LM_STUDIO_API_KEY` | LM Studio API key | `not-needed` |
| `OPENAI_API_KEY` | OpenAI API key | Required for OpenAI |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `MCP_HOST` | MCP server host | `localhost` |
| `MCP_PORT` | MCP server port | `8765` |
| `MEMORY_BASE_DIR` | Agent memory directory | `memory` |

### Configuration File

Edit `skills/mcp_config.yaml` for detailed configuration:

```yaml
llm:
  provider: "lm_studio"
  lm_studio:
    base_url: "http://localhost:1234/v1"
    api_key: "not-needed"
    model: "local-model"
    max_tokens: 1000
    temperature: 0.3
```

## Testing

### Run the Test Suite

```bash
# Run all MCP server tests
python -m pytest tests/test_mcp_server.py -v

# Run specific test categories
python -m pytest tests/test_mcp_server.py -v -k "memory"
python -m pytest tests/test_mcp_server.py -v -k "llm"
```

### Run the Demo

```bash
cd skills
python mcp_client_example.py
```

## LLM Provider Details

### LM Studio Setup

1. **Download**: Get LM Studio from [lmstudio.ai](https://lmstudio.ai/)
2. **Install Model**: Choose from Llama, Mistral, CodeLlama, etc.
3. **Start Server**: Enable "Start Server" in LM Studio
4. **Verify**: Server typically runs on `http://localhost:1234`

**Pros**:
- Local inference (no API costs)
- Privacy-focused
- Good performance with modern hardware
- No internet required

**Cons**:
- Requires local resources
- Model quality depends on hardware
- Slower than cloud APIs

### OpenAI Setup

1. **API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Set Environment**: `export OPENAI_API_KEY=your-key`
3. **Choose Model**: GPT-3.5-turbo, GPT-4, etc.

**Pros**:
- High-quality responses
- Fast inference
- No local resource requirements

**Cons**:
- Costs money per token
- Requires internet connection
- Data sent to OpenAI

### Mock Provider

Perfect for testing and development when you don't need real LLM responses.

**Pros**:
- No setup required
- Deterministic responses
- Zero cost
- Fast

**Cons**:
- Not useful for real analysis
- Limited response variety

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│  Legion MCP     │◄──►│  LLM Provider   │
│   (LLM Apps)    │    │     Server      │    │ (LM Studio/OAI) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Legion System   │
                       │ • Agents        │
                       │ • Memory        │
                       │ • Skills        │
                       │ • Tasks         │
                       └─────────────────┘
```

## Error Handling

The MCP server includes comprehensive error handling:

- **Graceful Degradation**: Falls back to mock provider if LLM unavailable
- **Retry Logic**: Automatic retries for transient failures  
- **Validation**: Input validation for all tool parameters
- **Logging**: Detailed logging for debugging

## Performance Considerations

- **Concurrent Requests**: Supports up to 100 concurrent MCP requests
- **Timeouts**: 30-second default timeout for LLM calls
- **Memory Usage**: Efficient memory management for agent data
- **Caching**: Optional caching for repeated requests

## Security

- **API Keys**: Secure handling of LLM API keys
- **Input Validation**: All inputs validated and sanitized
- **Error Information**: Sensitive data excluded from error messages
- **Local LLM**: LM Studio keeps data local for privacy

## Troubleshooting

### Common Issues

1. **"LLM not available"**
   - Check if LM Studio is running
   - Verify API endpoints and keys
   - Check network connectivity

2. **"Module not found" errors**
   - Ensure you're in the correct directory
   - Check Python path configuration
   - Verify all dependencies installed

3. **"Agent not found" errors**
   - Create agent memory directory
   - Initialize agent with some data first

4. **Slow responses**
   - Check LLM provider performance
   - Reduce max_tokens parameter
   - Use faster models

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python skills/mcp_server.py
```

## Contributing

See the main Legion contributing guidelines. The MCP server follows the same patterns and standards.

## License

Same license as the main Legion project. 