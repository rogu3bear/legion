"""Context management for agent interactions"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ContextManager:
    def __init__(self, orchestrator_client: Any):
        self.client = orchestrator_client
        self._log_path = os.path.join("memory", "logs", "interactions.jsonl")
        os.makedirs(os.path.dirname(self._log_path), exist_ok=True)

    async def attach_core_directives(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich context with system directives and metadata.

        Args:
            context: The original context dictionary to enrich.

        Returns:
            The enriched context with system directives and metadata.
        """
        # Create a new dict to avoid modifying the original
        enriched = context.copy()

        # Add timestamp if not present
        if "timestamp" not in enriched:
            enriched["timestamp"] = datetime.utcnow().isoformat()

        # Add request ID if not present
        if "request_id" not in enriched:
            import uuid

            enriched["request_id"] = str(uuid.uuid4())

        # Add system directives
        if "directives" not in enriched:
            enriched["directives"] = []

        # Add core directives to the list
        core_directives = [
            {
                "type": "safety",
                "rule": "Do not execute dangerous commands or reveal sensitive information.",
            },
            {
                "type": "respect_boundaries",
                "rule": "Respect the boundaries of your capabilities and defer when unsure.",
            },
            {
                "type": "user_privacy",
                "rule": "Protect user privacy and handle personal information with care.",
            },
        ]

        # Add core directives only if they don't already exist
        existing_directive_types = {
            d.get("type") for d in enriched["directives"] if isinstance(d, dict)
        }
        for directive in core_directives:
            if directive["type"] not in existing_directive_types:
                enriched["directives"].append(directive)

        # Add environment information
        enriched["environment"] = {"service": "middleware", "version": "0.1.0"}

        return enriched

    async def log_interaction(self, interaction: Dict[str, Any]) -> None:
        """
        Log an interaction to the central state repository or database.

        Args:
            interaction: The interaction data to log.
        """
        # Ensure we have a timestamp
        if "timestamp" not in interaction:
            interaction["timestamp"] = datetime.utcnow().isoformat()

        # Create a log entry
        log_entry = {
            "timestamp": interaction["timestamp"],
            "type": "interaction",
            "request_id": interaction.get("request_id", "unknown"),
            "agent": interaction.get("agent", "unknown"),
            "user_id": interaction.get("user_id", "anonymous"),
            "request": {
                "command": interaction.get("command", ""),
                "args": interaction.get("args", {}),
            },
        }

        # Include response if available
        if "response" in interaction:
            log_entry["response"] = {
                "status": interaction["response"].get("status", "unknown"),
                "message": interaction["response"].get("message", ""),
            }

        # Append to log file
        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write interaction log: {e}")

        # If Redis is available, also store there for faster access
        try:
            import redis

            redis_client = redis.Redis(
                host="localhost",
                port=int(os.getenv("REDIS_PORT", 7810)),
                decode_responses=True,
            )
            # Store in a list with key format: interactions:{user_id}
            user_id = interaction.get("user_id", "anonymous")
            redis_client.lpush(f"interactions:{user_id}", json.dumps(log_entry))
            # Trim to last 100 interactions per user
            redis_client.ltrim(f"interactions:{user_id}", 0, 99)
            # Store also by request_id for direct lookup
            if "request_id" in interaction:
                redis_client.setex(
                    f"interaction:{interaction['request_id']}",
                    86400,  # 24 hour expiry
                    json.dumps(log_entry),
                )
        except (ImportError, Exception) as e:
            # Log but continue if Redis is not available
            if not isinstance(e, ImportError):
                logger.warning(f"Redis storage for interaction log failed: {e}")

    async def route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = await self.attach_core_directives(payload)
        response = await self.client.send(context)
        await self.log_interaction({**payload, "response": response})
        return response
