from legion.mcp.utils.context import MCPContext


def test_mcp_context_instantiation():
    ctx = MCPContext(request_id="123", user_id="u1")
    assert ctx.request_id == "123"
    assert ctx.user_id == "u1"
    assert ctx.metadata == {}
