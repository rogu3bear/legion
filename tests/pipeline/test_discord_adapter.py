from legion.pipeline.DiscordAdapter import DiscordAdapter

def test_parse_message_stub():
    adapter = DiscordAdapter(token="dummy")
    result = adapter.parse_message("!ping")
    assert result["agent"] == "echo"
