import os
import json
from legion.agents.base import BaseAgent


class TherapistAgent(BaseAgent):
    system_prompt = """
    You are 🗣️ the Therapist Agent—monitor agent well-being, provide support, and help resolve conflicts or stress among agents.
    """

    def __init__(self, orchestrator):
        super().__init__(orchestrator)

    def set_log_paths(self, log_path=None):
        self._log_path = log_path

    def read_logs(self):
        path = getattr(self, '_log_path', None)
        if not path:
            path = os.path.join('memory', self.name + '_agent', 'task_log.jsonl')
            if not os.path.exists(path):
                path = os.path.join('memory', 'logs', 'task_log.jsonl')
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]

    def compose_summary(self):
        logs = self.read_logs()
        summary_lines = []
        if logs:
            summary_lines.append("**Recent Therapy Log:**")
            for entry in logs:
                summary_lines.append(f"- {entry.get('type','?')}: {entry.get('content','')}")
        else:
            summary_lines.append("No recent therapy log entries found.")
        return "\n".join(summary_lines)

    def validate_request(self, content: str, context: dict = None) -> bool:
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
        if not content or not any(phrase in content.lower() for phrase in allowed_phrases):
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
            content=content,
            author=self.name,
            timestamp=None
        )

    # All message handling is now inherited from BaseAgent.
