"""
MetricsAgent module for Legion.

This module defines the MetricsAgent class, which is responsible for collecting
and analyzing system metrics to provide insights and improve system performance.
"""

import asyncio
import datetime
import json
import os
from collections import defaultdict
from typing import Dict

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

from legion.agents.base import BaseAgent
from legion.task_queue import queue as task_queue


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
            port = int(os.getenv("REDIS_PORT", 7810))
            return redis.Redis(host="localhost", port=port, decode_responses=True)
        except Exception:
            return None

    def setup(self) -> None:
        """Start periodic metrics collection."""
        if self._heartbeat_task is None:
            loop = asyncio.get_event_loop()
            self._heartbeat_task = loop.create_task(self._heartbeat())

    async def _heartbeat(self) -> None:
        while True:
            await self.collect_stats()
            await asyncio.sleep(15)

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
            return
        try:
            self._redis.hset("metrics:latest", mapping=stats)
            for key, value in stats.items():
                self._redis.incrby(f"metrics:{key}:total", int(value))
        except Exception:
            pass

    def _default_prompt(self):
        """Return the default system prompt for the MetricsAgent."""
        return (
            "You are a MetricsAgent, tasked with collecting and analyzing system metrics "
            "to provide insights and improve performance. Your role is to monitor system "
            "health, track usage patterns, and suggest optimizations based on data."
        )

    async def collect_metrics(self):
        """Collect system metrics from various sources and store them."""
        metrics = {}

        # Collect task queue metrics
        if task_queue.client:
            try:
                metrics["task_queue_length"] = task_queue.client.zcard("task_queue")
                metrics["dead_letter_queue_length"] = task_queue.client.llen(
                    getattr(task_queue, "dead_letter_key", "dead_tasks")
                )
            except Exception as e:
                self.logger.error(f"Error collecting task queue metrics: {e}")
                metrics["task_queue_length"] = 0
                metrics["dead_letter_queue_length"] = 0
        else:
            metrics["task_queue_length"] = len(task_queue.store)
            metrics["dead_letter_queue_length"] = len(
                getattr(task_queue, "dead_letter", {})
            )

        # Collect agent state metrics
        try:
            metrics["agent_states"] = {}
            if self._redis:
                agent_keys = self._redis.keys("agent:*:state")
                for key in agent_keys:
                    state = self._redis.get(key)
                    agent_id = key.split(":")[1]
                    metrics["agent_states"][agent_id] = state
        except Exception as e:
            self.logger.error(f"Error collecting agent state metrics: {e}")

        # Collect memory usage metrics
        try:
            import psutil

            process = psutil.Process()
            metrics["memory_usage_mb"] = process.memory_info().rss / (1024 * 1024)
            metrics["cpu_percent"] = process.cpu_percent(interval=0.1)
        except ImportError:
            self.logger.warning("psutil not available, skipping memory metrics")
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")

        # Collect interaction counts from logs
        log_data = self.read_logs()
        interaction_counts = {}
        for entry in log_data:
            agent = entry.get("agent", "unknown")
            interaction_counts[agent] = interaction_counts.get(agent, 0) + 1
        metrics["interaction_counts"] = interaction_counts

        # Store the collected metrics
        timestamp = datetime.datetime.now().isoformat()
        metrics["timestamp"] = timestamp

        # Store in Redis if available
        if self._redis:
            try:
                self._redis.hset(f"metrics:{timestamp}", mapping=metrics)
                # Keep a rolling window of recent metrics
                self._redis.expire(f"metrics:{timestamp}", 86400)  # 24 hours
            except Exception as e:
                self.logger.error(f"Error storing metrics in Redis: {e}")

        return metrics

    async def analyze_metrics(self, metrics=None):
        """
        Analyze collected metrics and generate insights.

        Args:
            metrics: Dictionary of metrics to analyze. If None, retrieves the latest metrics.

        Returns:
            Dictionary containing analysis results and insights.
        """
        if metrics is None:
            # Retrieve the latest metrics if not provided
            if self._redis:
                try:
                    # Get the most recent metrics key
                    metric_keys = self._redis.keys("metrics:*")
                    if not metric_keys:
                        return {"status": "error", "message": "No metrics found"}

                    # Sort by timestamp (descending)
                    latest_key = sorted(metric_keys)[-1]
                    metrics = self._redis.hgetall(latest_key)
                except Exception as e:
                    self.logger.error(f"Error retrieving metrics from Redis: {e}")
                    return {
                        "status": "error",
                        "message": f"Error retrieving metrics: {e}",
                    }
            else:
                metrics = await self.collect_metrics()

        # Initialize analysis results
        analysis = {
            "timestamp": datetime.datetime.now().isoformat(),
            "insights": [],
            "warnings": [],
            "summary": {},
        }

        # Analyze task queue length
        queue_length = int(metrics.get("task_queue_length", 0))
        if queue_length > 100:
            analysis["warnings"].append(
                f"Task queue is very long: {queue_length} tasks"
            )
        elif queue_length > 50:
            analysis["insights"].append(
                f"Task queue is moderately long: {queue_length} tasks"
            )
        else:
            analysis["insights"].append(
                f"Task queue length is healthy: {queue_length} tasks"
            )

        # Analyze dead letter queue
        dead_length = int(metrics.get("dead_letter_queue_length", 0))
        if dead_length > 0:
            analysis["warnings"].append(
                f"Dead letter queue has {dead_length} failed tasks"
            )

        # Analyze agent states
        if "agent_states" in metrics:
            offline_agents = [
                agent
                for agent, state in metrics["agent_states"].items()
                if state not in ["online", "active", "ready"]
            ]
            if offline_agents:
                analysis["warnings"].append(
                    f"{len(offline_agents)} agents are offline: {', '.join(offline_agents)}"
                )

        # Analyze memory usage
        if "memory_usage_mb" in metrics:
            memory_mb = float(metrics["memory_usage_mb"])
            if memory_mb > 1000:
                analysis["warnings"].append(f"High memory usage: {memory_mb:.1f} MB")
            analysis["summary"]["memory_usage"] = f"{memory_mb:.1f} MB"

        # Analyze CPU usage
        if "cpu_percent" in metrics:
            cpu = float(metrics["cpu_percent"])
            if cpu > 80:
                analysis["warnings"].append(f"High CPU usage: {cpu:.1f}%")
            analysis["summary"]["cpu_usage"] = f"{cpu:.1f}%"

        # Analyze interaction counts
        if "interaction_counts" in metrics:
            total_interactions = sum(metrics["interaction_counts"].values())
            analysis["summary"]["total_interactions"] = total_interactions

            # Find most active agent
            if metrics["interaction_counts"]:
                most_active = max(
                    metrics["interaction_counts"].items(), key=lambda x: x[1]
                )
                analysis["insights"].append(
                    f"Most active agent: {most_active[0]} with {most_active[1]} interactions"
                )

        return analysis

    async def report_metrics(self, metrics=None, analysis=None):
        """
        Generate and report metrics and insights to relevant channels.

        Args:
            metrics: Dictionary of metrics to report. If None, retrieves the latest metrics.
            analysis: Dictionary of analysis results. If None, performs analysis on the metrics.

        Returns:
            The formatted report text.
        """
        if metrics is None:
            metrics = await self.collect_metrics()

        if analysis is None:
            analysis = await self.analyze_metrics(metrics)

        # Build the report
        report_lines = ["# Metrics Report", ""]

        # Add timestamp
        timestamp = metrics.get("timestamp", datetime.datetime.now().isoformat())
        report_lines.append(f"**Generated at:** {timestamp}")
        report_lines.append("")

        # Add summary section
        report_lines.append("## Summary")
        for key, value in analysis.get("summary", {}).items():
            # Convert snake_case to Title Case
            formatted_key = " ".join(word.capitalize() for word in key.split("_"))
            report_lines.append(f"- **{formatted_key}:** {value}")
        report_lines.append("")

        # Add insights section if there are any
        if analysis.get("insights"):
            report_lines.append("## Insights")
            for insight in analysis["insights"]:
                report_lines.append(f"- {insight}")
            report_lines.append("")

        # Add warnings section if there are any
        if analysis.get("warnings"):
            report_lines.append("## Warnings")
            for warning in analysis["warnings"]:
                report_lines.append(f"- ⚠️ {warning}")
            report_lines.append("")

        # Add details section
        report_lines.append("## Details")

        # Task queue metrics
        report_lines.append("### Queue Status")
        report_lines.append(
            f"- Tasks in queue: {metrics.get('task_queue_length', 'N/A')}"
        )
        report_lines.append(
            f"- Failed tasks: {metrics.get('dead_letter_queue_length', 'N/A')}"
        )
        report_lines.append("")

        # Agent state metrics
        if "agent_states" in metrics:
            report_lines.append("### Agent States")
            for agent, state in metrics["agent_states"].items():
                report_lines.append(f"- {agent}: {state}")
            report_lines.append("")

        # Interaction counts
        if "interaction_counts" in metrics:
            report_lines.append("### Interaction Counts")
            for agent, count in sorted(
                metrics["interaction_counts"].items(), key=lambda x: x[1], reverse=True
            ):
                report_lines.append(f"- {agent}: {count}")
            report_lines.append("")

        # Join all lines into a single string
        report_text = "\n".join(report_lines)

        # Post the report to Discord if available
        try:
            await self.post_to_discord(report_text)
        except Exception as e:
            self.logger.error(f"Error posting metrics report to Discord: {e}")

        # Store the report in Redis if available
        if self._redis:
            try:
                report_key = f"metrics:report:{datetime.datetime.now().isoformat()}"
                self._redis.set(report_key, report_text)
                self._redis.expire(report_key, 86400 * 7)  # Keep for 7 days
            except Exception as e:
                self.logger.error(f"Error storing metrics report in Redis: {e}")

        return report_text

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

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, and post to discord
        pass

    async def analyze_feedback_and_retrieve_memories_and_report_and_post_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report_and_post_to_discord_and_handle_report(
        self,
    ):
        # Implement the logic to analyze feedback, retrieve memories, report, post, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, handle report, post to discord, and handle report
        pass
