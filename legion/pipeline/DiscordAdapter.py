from __future__ import annotations

# ruff: noqa: N999
from dataclasses import dataclass
from typing import Any

from .Middleware import Middleware
from .schemas import InternalRequest


@dataclass
class ParsedCommand:
    command: str
    args: dict[str, Any]
    user: str


def parse_command(text: str) -> ParsedCommand:
    parts = text.strip().split()
    command = parts[0] if parts else ""
    args = {"raw": " ".join(parts[1:])}
    user = "anonymous"
    return ParsedCommand(command=command, args=args, user=user)


def determine_agent(channel_id: str, command: str) -> str:
    mapping = {"!metrics": "metrics"}
    return mapping.get(command, "metrics")


class DiscordAdapter:
    """Minimal adapter between Discord messages and the pipeline."""

    @staticmethod
    def on_message_receive(raw_text: str, channel_id: str) -> None:
        parsed = parse_command(raw_text)
        target_agent = determine_agent(channel_id, parsed.command)
        request = InternalRequest(
            user_id=parsed.user,
            command=parsed.command,
            args=parsed.args,
            channel=channel_id,
            agent_key=target_agent,
        )
        Middleware.process(request)

    @staticmethod
    def send_message(channel_id: str, text: str) -> None:
        if hasattr(Middleware, "client") and Middleware.client:
            channel = Middleware.client.get_channel(channel_id)
            if channel:
                Middleware.client.loop.create_task(channel.send(text))
                return
        print(f"[Discord:{channel_id}] {text}")
