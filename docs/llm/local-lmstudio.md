# LM Studio Local LLM Integration

This guide explains how to set up and use LM Studio as a local LLM provider for the Legion system.

## Overview

The Legion system includes an LM Studio MCP (Model Context Protocol) bridge that enables local LLM inference without external API dependencies. This is ideal for:

- **Privacy**: Keep all data processing local
- **Cost**: No per-token charges
- **Performance**: Reduced latency for local inference
- **Development**: Work offline without external API limits

## Prerequisites

- LM Studio installed on your system
- A compatible model downloaded in LM Studio
- Python 3.10+ with Legion requirements installed

## Installation & Setup

### 1. Install LM Studio

Download and install LM Studio from [https://lmstudio.ai](https://lmstudio.ai)

### 2. Download a Model

1. Open LM Studio
2. Navigate to the "Discovery" tab
3. Download a compatible model (recommended: `meta-llama-3.1-8b-instruct` or similar)

### 3. Start LM Studio Server

**Headless Mode (Recommended for Legion):**

```bash
# Start LM Studio server in headless mode
lmstudio server start --port 1234 --host 127.0.0.1
```

**GUI Mode:**

1. Open LM Studio application
2. Go to "Local Server" tab
3. Select your downloaded model
4. Click "Start Server"
5. Note the server address (default: `http://127.0.0.1:1234`)

### 4. Configure Legion

Set your environment variables in `.env`:

```env
# LLM Mode: 'local' for LM Studio, 'remote' for OpenAI/cloud providers
LLM_MODE=local

# Base URL for local LLM Studio
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1

# LM Studio MCP Bridge Port
LMSTUDIO_MCP_PORT=8009

# Model selection (must match model loaded in LM Studio)
OPENAI_MODEL=meta-llama-3.1-8b-instruct

# Enable LLM calls
ENABLE_LLM_CALLS=true
```

## Usage

### Starting the Legion System

1. Ensure LM Studio server is running
2. Start Legion orchestrator:

```bash
python -m legion.orchestrator
```

The system will automatically:
- Register the LM Studio MCP service
- Connect to LM Studio at `http://localhost:1234`
- Route LLM requests through the local bridge

### API Endpoints

The LM Studio MCP bridge exposes these endpoints:

- `POST /v1/chat/completions` - Chat completion requests
- `POST /v1/generate` - Raw generation requests
- `GET /health` - Health check and statistics
- `GET /models` - List available models

### Testing the Integration

Test the connection manually:

```bash
# Test chat completions
curl -X POST http://localhost:1234/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "meta-llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Test health endpoint
curl http://localhost:8009/health
```

## Troubleshooting

### Common Issues

**Connection Refused:**
- Verify LM Studio server is running on port 1234
- Check firewall settings
- Ensure model is loaded in LM Studio

**Model Not Found:**
- Verify the `OPENAI_MODEL` in `.env` matches the model loaded in LM Studio
- Check LM Studio model list with: `curl http://localhost:1234/v1/models`

**Performance Issues:**
- Ensure sufficient RAM (8GB+ recommended for 8B models)
- Consider using GPU acceleration if available
- Monitor system resources during inference

### Logs

Check Legion logs for LM Studio MCP activity:

```bash
# View orchestrator logs
tail -f scripts/logs/orchestrator.log

# Check for LM Studio MCP registration
grep "LM Studio MCP" scripts/logs/orchestrator.log
```

### Health Check

Monitor the LM Studio MCP bridge status:

```bash
# Check health endpoint
curl http://localhost:8009/health

# Expected response:
{
  "status": "healthy",
  "base_url": "http://127.0.0.1:1234/v1",
  "models_available": 1,
  "models": {"data": [...]}
}
```

## Advanced Configuration

### Multiple Models

LM Studio supports loading multiple models. Switch between them by updating the `OPENAI_MODEL` environment variable.

### Custom Ports

To use different ports:

```env
# Custom LM Studio port
LMSTUDIO_BASE_URL=http://127.0.0.1:1235/v1

# Custom MCP bridge port
LMSTUDIO_MCP_PORT=8010
```

### Resource Limits

Configure LM Studio server limits:

```bash
# Start with specific resource limits
lmstudio server start --port 1234 --host 127.0.0.1 --max-requests 10
```

## Security Considerations

- LM Studio server binds to localhost (127.0.0.1) by default
- MCP bridge only accepts local connections
- No external network exposure unless explicitly configured
- Model data remains local to your system

## Next Steps

- [Agent Configuration](../agents/) - Configure agents to use local LLM
- [Skills Integration](../skills/) - Add LLM-powered skills
- [Monitoring](../monitoring/) - Monitor local LLM performance
