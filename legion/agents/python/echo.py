"""Echo agent implementation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from legion.agents.base import BaseAgent
from legion.utils.discord_bridge import send_discord_embed, MessageType

AGENT_FEED_CHANNEL_ID = 1362902052279291904


class EchoAgent(BaseAgent):
    """Simple agent that mirrors incoming messages and persists a log."""

    system_prompt = (
        "You are \U0001f501 the Echo Agent—repeat back any message you receive, "
        "useful for diagnostics and testing message flow."
    )

    def __init__(self, name: str = "echo", config: Optional[dict] = None, orchestrator_ref: Optional[Any] = None, llm_client: Optional[Any] = None) -> None:
        super().__init__(name=name, config=config or {}, llm_client=llm_client)
        self.orchestrator = orchestrator_ref
        self.log_buffer: list[dict[str, Any]] = []
        log_dir = Path("memory") / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / "echo_agent.jsonl"



    def _flush_buffer(self) -> None:
        if not self.log_buffer:
            return
        with open(self.log_file, "a", encoding="utf-8") as f:
            for entry in self.log_buffer:
                f.write(json.dumps(entry) + "\n")
        self.log_buffer.clear()

    async def echo_task(self, message: str) -> str:
        """Handles the 'echo_task' skill: echoes the message and logs to agent-feed."""
        timestamp_utc = datetime.now(timezone.utc)
        entry = {
            "timestamp": timestamp_utc.isoformat(),
            "message": message,
            "skill": "echo_task"
        }
        self.log_buffer.append(entry)
        if len(self.log_buffer) >= 10:
            self._flush_buffer()
        
        result = f"Echoed: {message}"
        await self.log_to_feed(
            skill_name="echo_task",
            status="✅ Success",
            input_summary=message,
            output_summary=result,
            message_type=MessageType.SUCCESS
        )
        return result

    async def log_payload(self, payload: Any) -> dict:
        """Handles the 'log_payload' skill: logs the payload and reports to agent-feed."""
        timestamp_utc = datetime.now(timezone.utc)
        entry = {
            "timestamp": timestamp_utc.isoformat(),
            "payload": payload,
            "skill": "log_payload"
        }
        self.log_buffer.append(entry)
        if len(self.log_buffer) >= 10:
            self._flush_buffer()

        result = {"status": "payload logged successfully"}
        await self.log_to_feed(
            skill_name="log_payload",
            status="✅ Success",
            input_summary=payload,
            output_summary=result,
            message_type=MessageType.SUCCESS
        )
        return result

    async def handle_task(self, payload: dict) -> dict:
        """Dispatches a task to the correct skill method based on function_tag."""
        function_tag = payload.get("function_tag")
        result = None
        status = "✅ Success"
        error = None
        try:
            if function_tag == "echo_task":
                message = payload.get("message")
                result = await self.echo_task(message)
            elif function_tag == "log_payload":
                payload_data = payload.get("payload")
                result = await self.log_payload(payload_data)
            else:
                status = "❌ Unknown function_tag"
                error = f"Unknown function_tag: {function_tag}"
                result = None
                await self.log_to_feed(
                    skill_name=function_tag or "<missing>",
                    status=status,
                    input_summary=payload,
                    output_summary=error,
                    message_type=MessageType.ERROR
                )
                return {"status": status, "error": error}
            await self.log_to_feed(
                skill_name=function_tag,
                status=status,
                input_summary=payload,
                output_summary=result,
                message_type=MessageType.SUCCESS
            )
            return {"status": status, "result": result}
        except Exception as e:
            status = "❌ Exception"
            error = str(e)
            await self.log_to_feed(
                skill_name=function_tag or "<missing>",
                status=status,
                input_summary=payload,
                output_summary=error,
                message_type=MessageType.ERROR
            )
            return {"status": status, "error": error}

    def close(self) -> None:
        """Flush remaining logs when the agent is disposed."""
        self._flush_buffer()
