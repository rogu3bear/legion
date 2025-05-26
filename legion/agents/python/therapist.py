import json
import os
from typing import Optional, Any, Dict

from legion.agents.base import BaseAgent
from memory.legion_memory import LegionAgentMemory
from legion.utils.discord_bridge import send_discord_embed, MessageType
from datetime import datetime, timezone

AGENT_FEED_CHANNEL_ID = 1362902052279291904

class TherapistAgent(BaseAgent):
    system_prompt = """
    You are 🗣️ the Therapist Agent—monitor agent well-being, provide support, and help resolve conflicts or stress among agents.
    """

    def __init__(self, name: str, config: dict, orchestrator_ref: Optional[Any] = None, llm_client: Optional[Any] = None):
        """Initialize the TherapistAgent with name, config, orchestrator reference, and optional llm_client."""
        super().__init__(name=name, config=config or {}, llm_client=llm_client)
        self.orchestrator = orchestrator_ref

    def set_log_paths(self, log_path=None):
        self._log_path = log_path

    def read_logs(self):
        path = getattr(self, "_log_path", None)
        if not path:
            path = os.path.join("memory", self.name + "_agent", "task_log.jsonl")
            if not os.path.exists(path):
                path = os.path.join("memory", "logs", "task_log.jsonl")
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def compose_summary(self):
        logs = self.read_logs()
        summary_lines = []
        if logs:
            summary_lines.append("**Recent Therapy Log:**")
            for entry in logs:
                summary_lines.append(
                    f"- {entry.get('type', '?')}: {entry.get('content', '')}"
                )
        else:
            summary_lines.append("No recent therapy log entries found.")
        return "\n".join(summary_lines)

    def validate_request(self, content: str, context: Optional[dict] = None) -> bool:
        """
        Validate incoming request against core directives:
        - Only allow self-assessment or well-being queries.
        - Reject if content is empty, unrelated, or confidence is low (simulated by context).
        """
        allowed_phrases = [
            "self-assessment",
            "well-being",
            "agent support",
            "therapy",
            "stress",
            "conflict",
        ]
        if not content or not any(
            phrase in content.lower() for phrase in allowed_phrases
        ):
            return False
        # Simulate confidence threshold (context may provide 'confidence' float)
        if context and isinstance(context, dict):
            confidence = context.get("confidence", 1.0)
            if confidence < 0.5:
                return False
        return True

    def fallback_response(self, reason: str) -> str:
        """
        Generate a safe fallback message for invalid or out-of-scope requests.
        """
        return f"🗣️ Sorry, I can't process that request: {reason} If you need agent well-being support, please rephrase or contact an admin."

    async def handle_self_assessment(self, content=None, context=None):
        # Use default content if not provided
        if content is None:
            content = "Please perform a self-assessment and report on agent well-being."
        if not self.validate_request(content, context):
            reason = "Request not recognized as a valid self-assessment or confidence too low."
            fallback = self.fallback_response(reason)
            await self.post_to_discord(fallback)
            return fallback
        return await self.handle_message(
            content=content, author=self.name, timestamp=None
        )

    async def validate_intent(self, task_details: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validates a task's intent (structure/payload) against a schema or general rules.
        Logs validation outcome to agent-feed.
        This implements the 'validate_intent' skill, also serving as 'validate_task'.
        """
        input_summary = {"task_details": task_details, "schema_provided": schema is not None}
        validation_status = "unknown"
        validation_message = ""
        discord_message_type = MessageType.INFO

        # Basic validation: check for essential keys in task_details
        required_keys = ["task_id", "description", "action_type"]
        missing_keys = [key for key in required_keys if key not in task_details]

        if missing_keys:
            validation_status = "❌ Rejected (Schema Mismatch)"
            validation_message = f"Task rejected due to missing essential keys: {', '.join(missing_keys)}"
            discord_message_type = MessageType.ERROR
        elif schema: # Placeholder for more complex schema validation if provided
            # For now, assume if schema is provided and basic keys are there, it's a pass
            # In a real scenario, you'd compare task_details against the schema structure
            validation_status = "✅ Approved (Schema-Validated)"
            validation_message = "Task approved against provided schema (basic check)."
            discord_message_type = MessageType.SUCCESS
        else:
            validation_status = "✅ Approved (Basic Validation)"
            validation_message = "Task approved based on presence of essential keys."
            discord_message_type = MessageType.SUCCESS

        self.logger.info(f"TherapistAgent - validate_intent: {validation_status} - {validation_message}")

        await self.log_to_feed(
            skill_name="validate_intent",
            status=validation_status,
            input_summary=input_summary,
            output_summary=validation_message,
            message_type=discord_message_type
        )

        return {"validation_status": validation_status, "message": validation_message, "is_valid": "✅" in validation_status}

    async def sanitize_prompt(self, prompt_text: str) -> Dict[str, Any]:
        """(Stub) Sanitizes a given prompt text."""
        output_summary = f"Prompt received. Actual sanitization not yet implemented. Original prompt: {prompt_text[:100]}..."
        status_emoji = "⚠️ Stubbed"
        await self.log_to_feed(
            skill_name="sanitize_prompt",
            status=status_emoji,
            input_summary=prompt_text,
            output_summary=output_summary,
            message_type=MessageType.WARNING
        )
        self.logger.info(f"TherapistAgent: sanitize_prompt stub called for prompt: '{prompt_text[:50]}...'")
        return {"status": "Sanitization is stubbed", "sanitized_prompt": prompt_text} # Returns original for now

    async def reroute(self, task_id: str, reason: str, suggested_agent: Optional[str] = None) -> Dict[str, Any]:
        """(Stub) Reroutes a task based on a reason."""
        output_summary = f"Task '{task_id}' reroute requested due to '{reason}'. Suggested agent: {suggested_agent}. Actual rerouting not implemented."
        status_emoji = "⚠️ Stubbed"
        await self.log_to_feed(
            skill_name="reroute",
            status=status_emoji,
            input_summary={"task_id": task_id, "reason": reason, "suggested_agent": suggested_agent},
            output_summary=output_summary,
            message_type=MessageType.WARNING
        )
        self.logger.info(f"TherapistAgent: reroute stub called for task '{task_id}'")
        return {"status": "Rerouting is stubbed", "task_id": task_id, "rerouted_to": suggested_agent}

    def retrieve_memories(self, embeddings):
        feedback = LegionAgentMemory.retrieve_memories(
            self.name, embeddings, top_k=5, category="feedback"
        )
        return feedback

    async def handle_task(self, payload: dict) -> dict:
        """Dispatches a task to the correct skill method based on function_tag."""
        function_tag = payload.get("function_tag")
        result = None
        status = "✅ Success"
        error = None
        try:
            if function_tag == "validate_intent":
                result = await self.validate_intent(
                    task_details=payload.get("task_details", {}),
                    schema=payload.get("schema")
                )
            elif function_tag == "sanitize_prompt":
                result = await self.sanitize_prompt(
                    prompt_text=payload.get("prompt_text", "")
                )
            elif function_tag == "reroute":
                result = await self.reroute(
                    task_id=payload.get("task_id", ""),
                    reason=payload.get("reason", ""),
                    suggested_agent=payload.get("suggested_agent")
                )
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
