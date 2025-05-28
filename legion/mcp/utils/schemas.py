"""JSON schema stubs for MCP communication."""

MCPRequestSchema = {
    "type": "object"
    "properties": {
        "service": {"type": "string"}
        "payload": {"type": "object"}
    }
    "required": ["service", "payload"]
}

MCPResponseSchema = {
    "type": "object"
    "properties": {
        "status": {"type": "string"}
        "data": {"type": "object"}
    }
    "required": ["status"]
}

MCPErrorSchema = {
    "type": "object"
    "properties": {
        "error": {"type": "string"}
        "code": {"type": "integer"}
    }
    "required": ["error"]
}
