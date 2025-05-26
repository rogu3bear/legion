# Security Features

## Debug Mode Protection

Legion includes a `DEBUG` flag that controls access to development-only endpoints.

### Configuration

Set the `DEBUG` environment variable to control debug mode:

```bash
# Enable debug mode (development only)
export DEBUG=true

# Disable debug mode (production - default)
export DEBUG=false
```

### Protected Endpoints

When `DEBUG=false` (default), the following endpoints are disabled:

- `/api/demo/*` - Demo endpoints for testing without authentication

### Usage

In production environments, ensure `DEBUG` is set to `false` or left unset to prevent unauthorized access to development endpoints.

## Rate Limiting

### LM Studio Proxy Rate Limiting

The LM Studio proxy endpoints include built-in rate limiting to prevent abuse:

- **Endpoint**: `/api/v1/lmstudio/chat`
- **Limit**: 10 requests per minute per IP address
- **Response**: HTTP 429 "Too Many Requests" when limit exceeded

### Rate Limit Response Format

When rate limit is exceeded, the API returns:

```json
{
  "detail": {
    "error": "Too Many Requests",
    "message": "Rate limit exceeded. Maximum 10 requests per 60 seconds.",
    "retry_after": 60
  }
}
```

### Configuration

Rate limiting parameters are configured in `interface/api/v1/endpoints/lmstudio_proxy.py`:

```python
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60    # seconds
```

## File Locking

### Prompt File Locking

Prompt file operations include file locking to prevent concurrent write conflicts:

- **Implementation**: Uses `portalocker` for cross-platform file locking
- **Behavior**: Exclusive locks during write operations
- **Error Handling**: Returns HTTP 409 "Conflict" when file is locked

### Conflict Response

When a file lock conflict occurs:

```json
{
  "detail": "Prompt file is currently being modified by another process: agent_name"
}
```

## Best Practices

1. **Production Deployment**: Always set `DEBUG=false` in production
2. **Rate Limiting**: Monitor rate limit logs for potential abuse
3. **File Operations**: Handle HTTP 409 responses gracefully in client applications
4. **Security Headers**: The application includes security headers via middleware

## LM Studio Proxy Configuration

### Default max_tokens

The LM Studio proxy automatically sets a default `max_tokens` value when:
- The parameter is missing from the request
- The parameter is set to 0 or a negative value

**Default Value**: `256` tokens

This ensures that LM Studio receives a valid token limit and can generate proper completions.

### Stream Support

The proxy supports streaming responses when `stream=true` is set in the request:

- **Non-streaming**: Returns complete JSON response
- **Streaming**: Returns `StreamingResponse` with `application/x-ndjson` media type
- **Passthrough**: Streams chunks directly from LM Studio without buffering

### Known Error Codes

The proxy returns specific HTTP status codes for different error conditions:

- **429 Too Many Requests**: Rate limit exceeded (10 requests per minute per IP)
- **502 Bad Gateway**: LM Studio upstream connection failed
- **503 Service Unavailable**: LM Studio server unreachable
- **504 Gateway Timeout**: LM Studio request timeout (60 seconds)

### Error Response Format

Rate limit exceeded:
```json
{
  "detail": {
    "error": "Too Many Requests",
    "message": "Rate limit exceeded. Maximum 10 requests per 60 seconds.",
    "retry_after": 60
  }
}
```

Upstream errors:
```json
{
  "detail": "LM Studio connection failed: Connection refused"
}
```

For comprehensive LM Studio proxy documentation, see [docs/lmstudio_proxy.md](lmstudio_proxy.md).
