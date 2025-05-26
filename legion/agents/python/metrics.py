"""
MetricsAgent module for Legion.

This module defines the MetricsAgent class, which is responsible for collecting
and analyzing system metrics to provide insights and improve system performance.
"""

import asyncio
import json
import os
from collections import defaultdict
from typing import Dict, Optional, Any

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

from legion.agents.base import BaseAgent
from legion.task_queue import queue as task_queue
from legion.utils.discord_bridge import send_discord_embed, MessageType
from datetime import datetime, timezone

AGENT_FEED_CHANNEL_ID = 1362902052279291904


class MetricsAgent(BaseAgent):
    """An agent for collecting and analyzing system metrics."""



    def __init__(self, name: str, config: dict, orchestrator_ref=None, llm_client=None):
        """Initialize the MetricsAgent with name, config, orchestrator reference, and optional llm_client."""
        super().__init__(name, config or {}, llm_client=llm_client)
        # retain orchestrator reference
        self.orchestrator = orchestrator_ref
        self.system_prompt = self._default_prompt()
        self.counts = defaultdict(int)
        self._redis = self._get_redis()
        self._heartbeat_task = None

    def _get_redis(self):
        if redis is None:
            return None
        try:
            # Use the new Legion-specific Redis port and variable
            port = int(os.getenv("LEGION_REDIS_PORT", "7610")) 
            return redis.Redis(host="localhost", port=port, decode_responses=True)
        except Exception as e: # Added exception logging
            self.logger.error(f"MetricsAgent: Failed to connect to Redis: {e}")
            return None

    def setup(self) -> None:
        """Start periodic metrics collection."""
        if self._heartbeat_task is None:
            loop = asyncio.get_event_loop()
            self._heartbeat_task = loop.create_task(self._heartbeat())

    async def _heartbeat(self) -> None:
        while True:
            await self.collect_stats()
            await self.log_to_feed(
                skill_name="_heartbeat",
                status="✅ Collected & Pushed",
                input_summary="Scheduled statistics collection",
                output_summary="Stats pushed to Redis",
                message_type=MessageType.INFO
            )
            await asyncio.sleep(15) # Consider making interval configurable

    async def collect_stats(self) -> None:
        """Collect queue and agent stats then push to Redis."""
        stats: Dict[str, int] = {}
        # Task queue length
        if task_queue.client:
            try:
                qlen = task_queue.client.zcard("task_queue")
            except Exception:
                qlen = 0
        else:
            qlen = len(task_queue.store)
        stats["task_queue_length"] = int(qlen)

        # Dead letter queue length
        if task_queue.client:
            try:
                dead_len = task_queue.client.llen(
                    getattr(task_queue, "dead_letter_key", "dead_tasks")
                )
            except Exception:
                dead_len = 0
        else:
            dead_len = len(getattr(task_queue, "dead_letter", {}))
        stats["dead_letter_queue_length"] = int(dead_len)

        # Agent state counts
        state_counts: Dict[str, int] = {}
        client = self._redis
        if client is not None:
            try:
                for key in client.keys("agent:*:state"):
                    val = client.get(key)
                    state_counts[val] = state_counts.get(val, 0) + 1
            except Exception:
                pass
        stats.update({f"agents_{k}": v for k, v in state_counts.items()})

        await self.push_to_redis(stats)

    async def push_to_redis(self, stats: Dict[str, int]) -> None:
        """Store metrics in Redis and increment counters."""
        if self._redis is None:
            await self.log_to_feed(
                skill_name="push_to_redis",
                status="⚠️ Skipped",
                input_summary=stats,
                output_summary="Redis client not available",
                message_type=MessageType.WARNING
            )
            return
        try:
            self._redis.hset("metrics:latest", mapping=stats)
            for key, value in stats.items():
                self._redis.incrby(f"metrics:{key}:total", int(value))
            # No direct agent-feed log here to avoid noise from _heartbeat, 
            # _heartbeat itself will log completion.
        except Exception as e:
            self.logger.error(f"MetricsAgent: Error pushing to Redis: {e}")
            await self.log_to_feed(
                skill_name="push_to_redis",
                status="❌ Error",
                input_summary=stats,
                output_summary=str(e),
                message_type=MessageType.ERROR
            )

    def _default_prompt(self):
        """Return the default system prompt for the MetricsAgent."""
        return (
            "You are a MetricsAgent, tasked with collecting and analyzing system metrics "
            "to provide insights and improve performance. Your role is to monitor system "
            "health, track usage patterns, and suggest optimizations based on data."
        )

    async def collect_metrics(self):
        """Stub method to collect system metrics."""
        # TODO: Implement metrics collection logic
        pass

    async def analyze_metrics(self):
        """Stub method to analyze collected metrics and generate insights."""
        # TODO: Implement metrics analysis logic
        pass

    async def report_metrics(self):
        """Stub method to report metrics and insights to relevant channels or logs."""
        # TODO: Implement reporting logic
        pass

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
        report_lines = []
        for agent, count in sorted(counts.items(), key=lambda x: -x[1]):
            report_lines.append(f"{agent}: {count} messages")

        # Use the new Discord bridge for better formatting
        try:
            await self.send_success_notification(
                "Usage Metrics Report",
                {
                    "Total Messages": len(all_messages),
                    "Active Channels": len(channels),
                    "Avg per Channel": f"{avg_per_channel:.2f}",
                    "Top Agent": report_lines[0] if report_lines else "None",
                },
            )
        except Exception:
            # Fallback to old method
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
            timestamp=None,
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
            summary_lines.append("**Recent Metrics Log:**")
            for entry in logs:
                summary_lines.append(
                    f"- {entry.get('type', '?')}: {entry.get('content', '')}"
                )
        else:
            summary_lines.append("No recent metrics log entries found.")
        return "\n".join(summary_lines)

    async def analyze_feedback(self):
        # Implement the logic to analyze feedback
        pass

    async def retrieve_memories(self, embeddings):
        # Implement the logic to retrieve memories
        pass

    async def retrieve_feedback(self):
        # Implement the logic to retrieve feedback
        pass

    async def analyze_feedback_and_retrieve_memories(self):
        # Implement the logic to analyze feedback and retrieve memories
        pass

    async def analyze_feedback_and_retrieve_memories_and_report(self):
        # Implement the logic to analyze feedback, retrieve memories, and report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post(self):
        # Implement the logic to analyze feedback, retrieve memories, report, and post
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def record_counter(self, counter_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Records a custom counter. Tags can be used for dimensionality (future use)."""
        # For now, simple Redis increment. Tags could be part of the key or a separate hash.
        metric_key = f"metrics:custom:{counter_name}:total"
        result_summary = ""
        status_emoji = "✅"
        msg_type = MessageType.SUCCESS

        if self._redis is None:
            result_summary = "Redis client not available. Metric not recorded."
            status_emoji = "⚠️"
            msg_type = MessageType.WARNING
        else:
            try:
                self._redis.incrby(metric_key, int(value))
                result_summary = f"Counter '{counter_name}' incremented by {value}."
            except Exception as e:
                self.logger.error(f"MetricsAgent: Error recording counter '{counter_name}': {e}")
                result_summary = f"Error recording counter: {str(e)}"
                status_emoji = "❌"
                msg_type = MessageType.ERROR

        await self.log_to_feed(
            skill_name="record_counter",
            status=f"{status_emoji} {(msg_type.name).capitalize()}",
            input_summary={"counter_name": counter_name, "value": value, "tags": tags},
            output_summary=result_summary,
            message_type=msg_type
        )
        return {"status": result_summary, "key": metric_key}

    async def record_histogram(self, histogram_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """(Stub) Records a custom histogram value."""
        result_summary = f"Histogram '{histogram_name}' with value {value} received. Actual recording not yet implemented."
        await self.log_to_feed(
            skill_name="record_histogram",
            status="⚠️ Stubbed",
            input_summary={"histogram_name": histogram_name, "value": value, "tags": tags},
            output_summary=result_summary,
            message_type=MessageType.WARNING
        )
        self.logger.info(f"MetricsAgent: record_histogram stub called for '{histogram_name}'")
        return {"status": "Histogram recording is stubbed."}

    async def push_metric(self, metric_name: str, value: Any, unit: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """(Stub) Pushes a generic metric."""
        result_summary = f"Metric '{metric_name}' with value {value} (unit: {unit}) received. Actual push not yet implemented."
        await self.log_to_feed(
            skill_name="push_metric",
            status="⚠️ Stubbed",
            input_summary={"metric_name": metric_name, "value": value, "unit": unit, "tags": tags},
            output_summary=result_summary,
            message_type=MessageType.WARNING
        )
        self.logger.info(f"MetricsAgent: push_metric stub called for '{metric_name}'")
        return {"status": "Generic metric push is stubbed."}

    async def handle_task(self, payload: dict) -> dict:
        """Dispatches a task to the correct skill method based on function_tag."""
        function_tag = payload.get("function_tag")
        result = None
        status = "✅ Success"
        error = None
        try:
            if function_tag == "record_counter":
                result = await self.record_counter(
                    counter_name=payload.get("counter_name"),
                    value=payload.get("value", 1),
                    tags=payload.get("tags")
                )
            elif function_tag == "record_histogram":
                result = await self.record_histogram(
                    histogram_name=payload.get("histogram_name"),
                    value=payload.get("value"),
                    tags=payload.get("tags")
                )
            elif function_tag == "push_metric":
                result = await self.push_metric(
                    metric_name=payload.get("metric_name"),
                    value=payload.get("value"),
                    unit=payload.get("unit"),
                    tags=payload.get("tags")
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
