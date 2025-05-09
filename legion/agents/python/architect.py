import os
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from legion.agents.base import BaseAgent


class ArchitectAgent(BaseAgent):
    """Agent responsible for reviewing code and providing architectural guidance."""

    SYSTEM_PROMPT = """You are the Architect, a senior software engineer responsible for:
    1. Reviewing code changes and providing actionable feedback
    2. Ensuring architectural patterns are followed
    3. Monitoring system health and performance
    4. Guiding technical decisions
    """

    def __init__(self, orchestrator, llm_client=None):
        super().__init__(orchestrator, llm_client)
        # --- TEMP DEBUG LOGGING ---
        try:
            config_repr = repr(self.config)  # Get a representation
        except Exception as e:
            config_repr = f"Error getting config repr: {e}"
        self.logger.debug(f"[ARCHITECT_INIT_DEBUG] self.config = {config_repr}")
        # --- END TEMP DEBUG LOGGING ---
        # Determine repository path: prefer config entry for key without suffix, fallback to config key with suffix '_agent'
        if "repo_path" in self.config and self.config.get("repo_path"):
            self.repo_path = self.config.get("repo_path")
        else:
            agent_key = f"{self.name}_agent"
            # fallback to orchestrator.config for agent_key
            self.repo_path = self.orchestrator.config.get(agent_key, {}).get(
                "repo_path", "."
            )
        self.log_paths = []
        self.set_log_paths()

    async def handle_review(self, pr_diff=None):
        """Review code changes and provide feedback."""
        # Get file tree
        files = await self.list_repo()

        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Repository structure:\n{files}"},
        ]

        if pr_diff:
            messages.append(
                {"role": "user", "content": f"Changes to review:\n{pr_diff}"}
            )

        # Call LLM with specific parameters from config
        response = self.call_llm(
            thread_id="review",
            messages=messages,
            model=self.config.get("model"),
            temperature=self.config.get("review_temperature", 0.7),
            max_tokens=self.config.get("review_max_tokens", 2000),
        )

        # Post response to Discord
        await self.post_to_discord(response)

        return response

    async def list_repo(self):
        """Get list of files/dirs in repo."""

        def list_files(startpath):
            tree = []
            for root, dirs, files in os.walk(startpath):
                level = root.replace(startpath, "").count(os.sep)
                indent = "  " * level
                tree.append(f"{indent}{os.path.basename(root)}/")
                for f in files:
                    tree.append(f"{indent}  {f}")
            return "\n".join(tree)

        return list_files(self.repo_path)

    def set_log_paths(self):
        """Set paths to log files to monitor."""
        log_dir = os.path.join(self.repo_path, "logs")
        if os.path.exists(log_dir):
            self.log_paths = [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.endswith(".log")
            ]

    def read_logs(self, hours=24):
        """Read recent logs within specified hours."""
        # Use timezone aware datetime for cutoff
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        logs = []

        # --- TEMP DEBUG LOGGING ---
        self.logger.debug(f"[READ_LOGS_DEBUG] Cutoff time: {cutoff.isoformat()}")
        self.logger.debug(
            f"[READ_LOGS_DEBUG] Log paths being checked: {self.log_paths}"
        )
        if not self.log_paths:
            self.logger.warning("[READ_LOGS_DEBUG] No log paths found!")
        # --- END TEMP DEBUG LOGGING ---

        for path in self.log_paths:
            # --- TEMP DEBUG LOGGING ---
            self.logger.debug(f"[READ_LOGS_DEBUG] Checking path: {path}")
            if not os.path.exists(path):
                self.logger.warning(
                    f"[READ_LOGS_DEBUG] Log path does not exist: {path}"
                )
                continue
            # --- END TEMP DEBUG LOGGING ---
            try:
                with open(path) as f:
                    for line_num, line in enumerate(f, 1):
                        # --- TEMP DEBUG LOGGING ---
                        line_processed = False
                        # --- END TEMP DEBUG LOGGING ---
                        try:
                            # Assume ISO format timestamp at start of line
                            ts_str = line[
                                :26
                            ]  # Check length before slicing? No, handle ValueError
                            ts = datetime.fromisoformat(ts_str)
                            # Ensure ts is offset-aware for comparison
                            ts_aware = ts
                            if ts.tzinfo is None:
                                # Make naive datetime timezone-aware (assuming UTC)
                                ts_aware = ts.replace(tzinfo=timezone.utc)

                            # --- TEMP DEBUG LOGGING ---
                            is_after_cutoff = ts_aware > cutoff
                            self.logger.debug(
                                f"[READ_LOGS_DEBUG] Line {line_num}: Timestamp='{ts_aware.isoformat()}', Cutoff='{cutoff.isoformat()}', AfterCutoff={is_after_cutoff}"
                            )
                            # --- END TEMP DEBUG LOGGING ---

                            if is_after_cutoff:
                                logs.append(line.strip())
                                # --- TEMP DEBUG LOGGING ---
                                line_processed = True
                                # --- END TEMP DEBUG LOGGING ---
                        except ValueError:
                            # --- TEMP DEBUG LOGGING ---
                            self.logger.debug(
                                f"[READ_LOGS_DEBUG] Line {line_num}: Skipping line, ValueError parsing timestamp '{line[:26]}...'"
                            )
                            # --- END TEMP DEBUG LOGGING ---
                            continue  # Skip lines without valid timestamp prefix
                        # --- TEMP DEBUG LOGGING ---
                        finally:
                            if not line_processed:
                                self.logger.debug(
                                    f"[READ_LOGS_DEBUG] Line {line_num}: Did not meet cutoff condition."
                                )
                        # --- END TEMP DEBUG LOGGING ---

            except Exception as e:
                self.logger.error(f"Error reading log {path}: {e}")

        # --- TEMP DEBUG LOGGING ---
        self.logger.debug(
            f"[READ_LOGS_DEBUG] Finished reading logs. Found {len(logs)} entries."
        )
        # --- END TEMP DEBUG LOGGING ---
        return logs

    def extract_llm_metrics(self, logs):
        """Extract LLM-related metrics from logs."""
        metrics = {"total_calls": 0, "avg_latency": 0, "error_rate": 0}

        latencies = []
        errors = 0

        for log in logs:
            if "llm_call" in log:
                metrics["total_calls"] += 1
                # Extract latency if present
                if "latency=" in log:
                    try:
                        latency = float(log.split("latency=")[1].split()[0])
                        latencies.append(latency)
                    except:
                        pass
            if "llm_error" in log:
                errors += 1

        if latencies:
            metrics["avg_latency"] = sum(latencies) / len(latencies)
        if metrics["total_calls"]:
            metrics["error_rate"] = errors / metrics["total_calls"]

        return metrics

    async def compose_summary(self):
        """Compose summary of recent task logs and LLM metrics."""
        logs = self.read_logs(hours=24)
        metrics = self.extract_llm_metrics(logs)

        # Round average latency to 2 decimal places using half-up rounding
        avg_latency = Decimal(str(metrics["avg_latency"])).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )
        summary = [
            "System Health Summary",
            "-------------------",
            f"Total LLM calls: {metrics['total_calls']}",
            f"Average latency: {avg_latency}s",
            f"Error rate: {metrics['error_rate']:.2%}",
            "\nRecent Logs:",
            "------------",
        ]

        # Add last 10 logs
        summary.extend(logs[-10:])

        return "\n".join(summary)

    async def retrieve_feedback(self, query, k=5):
        """Retrieve relevant feedback memories based on embeddings."""
        if not self.memory:
            return []

        results = await self.memory.search(collection="feedback", query=query, k=k)

        return results
