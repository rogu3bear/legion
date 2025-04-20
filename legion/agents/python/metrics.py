import os
from collections import defaultdict
from legion.agents.base import BaseAgent
import json


class MetricsAgent(BaseAgent):
    system_prompt = """
    You are 📊 the Metrics Agent—track, analyze, and report on system and agent activity, usage, and performance metrics.
    """

    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        self.counts = defaultdict(int)

    async def report(self):
        # Fetch recent messages from all agent channels
        channels = self.get_agent_channels()
        all_messages = []
        for channel in channels:
            try:
                async for msg in channel.history(limit=50):
                    all_messages.append(msg)
            except Exception:
                continue
        # Tally messages per agent
        counts = dict(self.counts)
        for msg in all_messages:
            author = getattr(msg.author, "display_name", str(msg.author))
            counts[author] = counts.get(author, 0) + 1
        avg_per_channel = len(all_messages) / len(channels) if channels else 0
        # Format report
        lines = ["| Agent | Messages |", "|-------|----------|"]
        for agent, count in sorted(counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {agent} | {count} |")
        lines.append(f"\n**Average messages per channel:** {avg_per_channel:.2f}")
        report_text = "\n".join(lines)
        await self.post_to_discord("**Usage Metrics**\n" + report_text)

    async def handle_report(self):
        return await self.handle_message(
            content="Please generate a metrics report for the system.",
            author=self.name,
            timestamp=None
        )

    def get_agent_channels(self):
        # Get all agent channel IDs from env
        channel_ids = [
            os.getenv("GENERAL_CHANNEL_ID"),
            os.getenv("AGENT_FEED_CHANNEL_ID"),
            os.getenv("ARCHITECT_CHANNEL_ID"),
            os.getenv("METRICS_CHANNEL_ID"),
            os.getenv("THERAPIST_CHANNEL_ID"),
            os.getenv("DESIGN_CHANNEL_ID"),
        ]
        ids = [int(cid) for cid in channel_ids if cid and cid.isdigit()]
        return [
            self.client.get_channel(cid) for cid in ids if self.client.get_channel(cid)
        ]

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
            summary_lines.append("**Recent Metrics Log:**")
            for entry in logs:
                summary_lines.append(f"- {entry.get('type','?')}: {entry.get('content','')}")
        else:
            summary_lines.append("No recent metrics log entries found.")
        return "\n".join(summary_lines)
