```
class DiscordAdapter:
    def __init__(self, token: str):
        """Adapter that integrates a Discord client with Legion's routing logic."""
        self.token = token
        # TODO: Connect to actual Discord client (deferred to Cursor)

    def parse_message(self, message: str) -> dict:
        """Parses a Discord message and returns a task dictionary."""
        # TODO: Replace with NLP or command parsing logic
        return {
            "id": "temp-id",
            "agent": "echo",
            "payload": {"message": message},
        }

    def send_response(self, channel_id: str, content: str) -> None:
        """Placeholder for sending messages back to Discord."""
        # TODO: Connect to Discord bot API
        print(f"[DiscordAdapter] Sending to {channel_id}: {content}")
```

```
from legion.pipeline.DiscordAdapter import DiscordAdapter

def test_parse_message_stub():
    adapter = DiscordAdapter(token="dummy")
    result = adapter.parse_message("!ping")
    assert result["agent"] == "echo"
```
