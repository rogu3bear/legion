import json
import os

from legion.agents.base import BaseAgent
from core.therapist import therapist_guard


class ArchitectAgent(BaseAgent):
    """Agent responsible for reviewing code and providing architectural guidance."""

    SYSTEM_PROMPT = """You are the Architect, a senior software engineer responsible for:
    1. Reviewing code changes and providing actionable feedback
    2. Ensuring architectural patterns are followed
    3. Monitoring system health and performance
    4. Guiding technical decisions
    """

    def __init__(self, name: str, config: dict, orchestrator_ref=None, llm_client=None):
        super().__init__(name, config, llm_client)
        # assign orchestrator reference for internal use
        self.orchestrator = orchestrator_ref
        # --- TEMP DEBUG LOGGING ---
        try:
            config_repr = repr(self.config)  # Get a representation
        except Exception as e:
            config_repr = f"Error getting config repr: {e}"
        self.logger.debug(f"[ARCHITECT_INIT_DEBUG] self.config = {config_repr}")
        # --- END TEMP DEBUG LOGGING ---
        # Determine repository path; safely handle missing config or orchestrator
        try:
            if isinstance(self.config, dict) and self.config.get("repo_path"):
                self.repo_path = self.config["repo_path"]
            else:
                agent_key = f"{self.name}_agent"
                self.repo_path = (
                    getattr(self.orchestrator, "config", {})
                    .get(agent_key, {})
                    .get("repo_path", ".")
                )
        except Exception:
            self.repo_path = "."
        self.log_paths = []
        self.set_log_paths()

    @therapist_guard("directive")
    async def handle_review(self, pr_diff=None):
        """Review code changes and provide feedback."""
        # Get file tree
        files = await self.list_repo()

        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Repository structure:\n{files}"}
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
            max_tokens=self.config.get("review_max_tokens", 2000)
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

    def set_log_paths(self, log_path=None, report_path=None):
        """Set paths to task log and report log for reading logs and metrics."""
        # Task log path
        if log_path:
            self.task_log_path = log_path
        else:
            self.task_log_path = os.path.join(self.repo_path, "logs", "task_log.jsonl")
        # Report (metrics) log path
        if report_path:
            self.report_path = report_path
        else:
            self.report_path = os.path.join(
                self.repo_path, "logs", "llm_connector_test.log"
            )

    def read_logs(self):
        """Read JSONL task log entries."""
        entries = []
        try:
            with open(self.task_log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return entries

    def extract_llm_metrics(self):
        """Extract LLM-related metrics from report file."""
        latency = None
        errors = None
        try:
            with open(self.report_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("latency:"):
                        val = line.split("latency:")[1].strip()
                        if val.endswith("ms"):
                            val = val[:-2]
                        try:
                            latency = float(val)
                        except ValueError:
                            latency = None
                    elif line.startswith("errors:"):
                        try:
                            errors = int(line.split("errors:")[1].strip())
                        except ValueError:
                            errors = None
        except Exception:
            pass
        return {"latency": latency, "errors": errors}

    def compose_summary(self):
        """Compose summary of recent task logs and LLM metrics."""
        logs = self.read_logs()
        metrics = self.extract_llm_metrics()
        lines = []
        lines.append("**Recent Task Log:**")
        if logs:
            for entry in logs:
                lines.append(f"- {entry.get('type')}: {entry.get('content')}")
        else:
            lines.append("No recent log entries found.")
        lines.append("")
        lines.append("**LLM Metrics:**")
        lines.append(f"- latency: {metrics.get('latency')}")
        lines.append(f"- errors: {metrics.get('errors')}")
        return "\n".join(lines)

    async def retrieve_feedback(self, query, k=5):
        """Retrieve relevant feedback memories based on embeddings."""
        if not self.memory:
            return []

        results = await self.memory.search(collection="feedback", query=query, k=k)

        return results
