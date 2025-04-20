import os
import json
from legion.agents.base import BaseAgent


class ArchitectAgent(BaseAgent):
    def __init__(self, name, client, channel_id):
        super().__init__(name, client, channel_id)

    async def handle_review(self):
        # List the repo
        file_tree = self.list_repo()
        bullet_list = "\n".join(f"- {path}" for path in file_tree)
        system_msg = "You're an expert software architect. Given this file tree, explain the high-level structure and identify any potential gaps or refactoring opportunities."
        user_msg = f"File tree:\n{bullet_list}"
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
        # Call through centralized LLMClient
        response = self.call_llm(
            thread_id="review", history=messages, temperature=0.3, max_tokens=600
        )
        review_text = response
        await self.post_to_discord(review_text)

    def list_repo(self):
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../")
        )
        file_tree = []
        for root, dirs, files in os.walk(repo_root):
            for d in dirs:
                rel_path = os.path.relpath(os.path.join(root, d), repo_root)
                file_tree.append(rel_path + "/")
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), repo_root)
                file_tree.append(rel_path)
        return sorted(file_tree)

    def set_log_paths(self, log_path=None, report_path=None):
        self._log_path = log_path
        self._report_path = report_path

    def read_logs(self):
        path = getattr(self, '_log_path', None)
        if not path:
            # Default to agent-specific or global log
            path = os.path.join('memory', self.name + '_agent', 'task_log.jsonl')
            if not os.path.exists(path):
                path = os.path.join('memory', 'logs', 'task_log.jsonl')
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]

    def extract_llm_metrics(self):
        path = getattr(self, '_report_path', None)
        if not path:
            path = os.path.join('artifacts', 'reports', 'llm_connector_test.log')
        if not os.path.exists(path):
            return {}
        metrics = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if 'latency' in line:
                    try:
                        metrics['latency'] = float(line.split(':')[1].replace('ms','').strip())
                    except Exception:
                        pass
                if 'errors' in line:
                    try:
                        metrics['errors'] = int(line.split(':')[1].strip())
                    except Exception:
                        pass
        return metrics

    def compose_summary(self):
        logs = self.read_logs()
        metrics = self.extract_llm_metrics()
        summary_lines = []
        if logs:
            summary_lines.append("**Recent Task Log:**")
            for entry in logs:
                summary_lines.append(f"- {entry.get('type','?')}: {entry.get('content','')}")
        else:
            summary_lines.append("No recent log entries found.")
        if metrics:
            summary_lines.append("\n**LLM Metrics:**")
            for k, v in metrics.items():
                summary_lines.append(f"- {k}: {v}")
        else:
            summary_lines.append("No LLM metrics available.")
        return "\n".join(summary_lines)
