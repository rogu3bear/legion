import os
import json
from legion.agents.base import BaseAgent


class TherapistAgent(BaseAgent):
    def __init__(self, name, client, channel_id, config=None):
        super().__init__(name, client, channel_id, config=config)

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

    # All message handling is now inherited from BaseAgent.
