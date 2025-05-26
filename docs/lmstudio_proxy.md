# LM Studio Proxy Documentation

## Overview

The LM Studio proxy provides a standardized interface for interacting with local LM Studio instances through Legion's API. It includes robust error handling, rate limiting, privacy features, and comprehensive retry logic.

## API Endpoints

### POST `/api/v1/lmstudio/chat`

Structured chat endpoint that accepts standardized request format and forwards to LM Studio.

#### Request Schema

```json
{
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "Message content"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 256,
  "stream": false
}
```

#### Field Descriptions

- **`messages`** (required): Array of chat messages with role and content
- **`temperature`** (optional): Sampling temperature (0.0-2.0, default: 0.7)
- **`max_tokens`** (optional): Maximum tokens to generate (1-4096, default: 256)
- **`stream`** (optional): Return streaming SSE/NDJSON response (default: false)

#### Response Formats

**Non-streaming:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Generated response"
      }
    }
  ],
  "usage": {
    "completion_tokens": 15,
    "prompt_tokens": 10,
    "total_tokens": 25
  }
}
```

**Streaming:**
Server-sent events with `application/x-ndjson` content type.

### POST `/api/v1/lmstudio/echo`

Raw proxy endpoint that forwards arbitrary JSON payloads directly to LM Studio.

## Configuration

### Environment Variables

```env
# LM Studio server URL
LMSTUDIO_API_URL=http://127.0.0.1:1234/v1

# Debug mode (affects logging privacy)
DEBUG=false
```

### Timeout Configuration

- **Connect Timeout**: 10 seconds
- **Request Timeout**: 60 seconds
- **Retry Attempts**: 2 (with exponential backoff)

### Rate Limiting

- **Limit**: 10 requests per minute per IP address
- **Scope**: Applies to completed requests only
- **Streaming**: Rate limit registered after stream completion

## Features

### Automatic max_tokens Default

The proxy automatically sets `max_tokens=256` when:
- The parameter is missing from the request
- The parameter is set to 0 or a negative value
- The parameter exceeds the maximum limit (4096)

This ensures LM Studio receives valid parameters and can generate proper completions.

### Retry Logic

Connection errors and timeouts trigger automatic retries:

1. **First attempt**: Immediate request
2. **Retry 1**: After 0.5 second delay
3. **Retry 2**: After 1.0 second delay
4. **Final failure**: Return appropriate HTTP error

### Privacy-Safe Logging

When `DEBUG=false` (production mode):
- Message content is redacted in all log entries
- Logged payloads show `[REDACTED]` instead of actual content
- Request metadata (tokens, temperature) remains visible

Example redacted log:
```json
{
  "messages": [{"role": "user", "content": "[REDACTED]"}],
  "temperature": 0.7,
  "max_tokens": 256
}
```

### Error Handling

The proxy returns specific HTTP status codes:

- **400 Bad Request**: Invalid JSON payload
- **422 Unprocessable Entity**: Request validation error
- **429 Too Many Requests**: Rate limit exceeded
- **503 Service Unavailable**: LM Studio connection failed
- **504 Gateway Timeout**: Request timeout or LM Studio unreachable

## Usage Examples

### Basic Chat Request

```bash
curl -X POST http://localhost:8000/api/v1/lmstudio/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

### Streaming Request

```bash
curl -X POST http://localhost:8000/api/v1/lmstudio/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Tell me a story"}
    ],
    "stream": true,
    "max_tokens": 512
  }'
```

### Custom Parameters

```bash
curl -X POST http://localhost:8000/api/v1/lmstudio/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "temperature": 0.3,
    "max_tokens": 1024,
    "stream": false
  }'
```

## OpenAPI Integration

The proxy endpoints are fully documented in the OpenAPI schema available at `/openapi.json`. The schema includes:

- Complete field descriptions
- Validation rules and constraints
- Default values
- Example requests and responses

## Monitoring and Debugging

### Rate Limit Headers

Rate limit information is included in error responses:

```json
{
  "detail": {
    "error": "Too Many Requests",
    "message": "Rate limit exceeded. Maximum 10 requests per 60 seconds.",
    "retry_after": 60
  }
}
```

### Health Check

Monitor LM Studio connectivity through standard error responses. Connection failures will return 503 with details about the upstream error.

### Log Levels

- **DEBUG**: Request/response payloads (redacted in production)
- **INFO**: Request completion and timing
- **WARNING**: Retry attempts and recoverable errors
- **ERROR**: Failed requests and upstream errors

## Security Considerations

1. **Message Privacy**: Content redaction in production logs
2. **Rate Limiting**: IP-based request throttling
3. **Timeout Protection**: Prevents resource exhaustion
4. **Input Validation**: Schema-based request validation
5. **Error Boundaries**: Graceful handling of upstream failures
