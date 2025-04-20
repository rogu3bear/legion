import os
import glob
import yaml
import time
import logging
import logging.config
from memory.legion_memory import LegionAgentMemory
from dotenv import load_dotenv
import openai
logging.getLogger("openai").setLevel(logging.ERROR)
from core.utils.llm_client import LLMClient
import asyncio
import re
from integration.discord.cogs.ux_feed import render_feed_item
from legion.agents.python.doctor import DoctorAgent
from legion.agents.python.ping import PingAgent
from legion.agents.python.echo import EchoAgent
from legion.agents.python.healthcheck import HealthcheckAgent
from legion.agents.python.metrics import MetricsAgent
from legion.agents.python.ux_designer import UxDesignerAgent
from legion.agents.python.therapist import TherapistAgent
from legion.agents.python.architect import ArchitectAgent
import datetime
from pathlib import Path
import atexit
import signal
import sys

# Configure logging if a YAML config exists
LOGGING_CONFIG_PATH = os.path.join("config", "logging.yaml")
if os.path.exists(LOGGING_CONFIG_PATH):
    with open(LOGGING_CONFIG_PATH, "r") as f:
        logging_config = yaml.safe_load(f)
    logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Only load .env if OpenAI config is used
try:
    load_dotenv(dotenv_path=".env")
    # LM Studio override: read OPENAI_API_BASE and ensure /v1 prefix
    llm_base = os.getenv("OPENAI_API_BASE")
    if llm_base:
        # Ensure base URL includes /v1 prefix
        if not llm_base.rstrip("/").endswith("/v1"):
            llm_base = llm_base.rstrip("/") + "/v1"
        openai.api_base = llm_base
        openai.api_type = "openai"
    model = os.getenv("OPENAI_MODEL")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.5))
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 1000))
    top_p = float(os.getenv("OPENAI_TOP_P", 1))
    frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", 0))
    presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", 0))
except ImportError:
    pass

# Read Discord channel IDs from environment variables
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID", "0"))
AGENT_FEED_CHANNEL_ID = int(os.getenv("AGENT_FEED_CHANNEL_ID", "0"))
ARCHITECT_CHANNEL_ID = int(os.getenv("ARCHITECT_CHANNEL_ID", "0"))
METRICS_CHANNEL_ID = int(os.getenv("METRICS_CHANNEL_ID", "0"))
THERAPIST_CHANNEL_ID = int(os.getenv("THERAPIST_CHANNEL_ID", "0"))
DESIGN_CHANNEL_ID = int(os.getenv("DESIGN_CHANNEL_ID", "0"))

CHANNEL_ID_MAP = {
    "general_agent": GENERAL_CHANNEL_ID,
    "agent_feed_agent": AGENT_FEED_CHANNEL_ID,
    "architect_agent": ARCHITECT_CHANNEL_ID,
    "metrics_agent": METRICS_CHANNEL_ID,
    "therapist_agent": THERAPIST_CHANNEL_ID,
    "ux_designer_agent": DESIGN_CHANNEL_ID,
    "ping_agent": GENERAL_CHANNEL_ID,
    "echo_agent": GENERAL_CHANNEL_ID,
    "healthcheck_agent": GENERAL_CHANNEL_ID,
}

# Map agent names to their classes
CLASS_MAP = {
    "architect_agent": ArchitectAgent,
    "metrics_agent": MetricsAgent,
    "ux_designer_agent": UxDesignerAgent,
    "therapist_agent": TherapistAgent,
    "ping_agent": PingAgent,
    "echo_agent": EchoAgent,
    "healthcheck_agent": HealthcheckAgent,
}

PID_FILE = "/tmp/legion_orchestrator.pid"

class Orchestrator:
    """Stub orchestrator (AutoGen code removed)."""

    def __init__(self, post_agent_message=None, pid_file=None):
        self._pid_file = pid_file or PID_FILE
        self._lock_acquired = False
        self._acquire_lock()
        self._setup_signal_handlers()
        # Populate agent_channel_ids from agent_configs (YAML), fallback to env/channel map
        self.agent_channel_ids = {}
        for name in CLASS_MAP.keys():
            config = self.load_agent_configs().get(name, {})
            chan = config.get('discord_channel_id')
            if not chan:
                chan = CHANNEL_ID_MAP.get(name, 0)
            self.agent_channel_ids[name] = int(chan) if chan else 0
        self._post_agent_message = lambda agent, payload: None
        # Load agent configs and instantiate agents
        self.agent_configs = self.load_agent_configs()
        self.agents = {name: CLASS_MAP[name](self) for name in self.agent_configs.keys()}
        self._agent_objects = self.agents  # Backward compatibility for legacy tests

        self.agent_classes = CLASS_MAP
        self.memory = {name: LegionAgentMemory(name) for name in self.agent_classes}
        # Only use self.agents for all agent lookups and dispatches
        for name, agent in self.agents.items():
            agent.config = self.agent_configs.get(name, {})
            agent.llm = LLMClient(
                api_key=agent.config.get("llm_api_key"),
                model=agent.config.get("llm_model"),
                api_base=agent.config.get("llm_api_base"),
                **agent.config.get("default_kwargs", {}),
            )
            agent.dynamic_rules = agent.config.get("dynamic_rules", {})
        logger.info(
            "Orchestrator initialized with agents: %s", list(self.agent_configs.keys())
        )

    def _acquire_lock(self):
        if os.path.exists(self._pid_file):
            try:
                with open(self._pid_file, "r") as f:
                    pid = int(f.read().strip())
                # Check if process is alive (cross-platform best effort)
                if pid and pid != os.getpid():
                    try:
                        os.kill(pid, 0)
                        logger.info(f"Another orchestrator instance (PID {pid}) is already running. Exiting.")
                        sys.exit(1)
                        return
                        import builtins
                        if getattr(sys.exit, "__module__", None) == "sys":
                            os._exit(1)
                    except OSError:
                        logger.info(f"Stale PID file found. Overwriting lock.")
            except Exception:
                logger.info("Corrupt PID file. Overwriting lock.")
        with open(self._pid_file, "w") as f:
            f.write(str(os.getpid()))
        self._lock_acquired = True
        atexit.register(self._release_lock)
        logger.info(f"Acquired orchestrator lock (PID {os.getpid()}).")

    def _release_lock(self):
        if self._lock_acquired and os.path.exists(self._pid_file):
            try:
                os.remove(self._pid_file)
                logger.info("Released orchestrator lock and cleaned up PID file.")
            except Exception as e:
                logger.error(f"Failed to remove PID file: {e}")
        self._lock_acquired = False

    def _setup_signal_handlers(self):
        def handle_signal(signum, frame):
            logger.info(f"Received signal {signum}. Initiating graceful shutdown.")
            self._release_lock()
            sys.exit(0)
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    def _get_channel_id(self, agent_name):
        return CHANNEL_ID_MAP.get(agent_name, GENERAL_CHANNEL_ID)

    def load_agent_configs(self):
        """Loads agent configurations from YAML files."""
        registry = {}
        agent_config_dir = Path(__file__).parent / "configs"
        print(f"[DEBUG] Scanning agent config dir: {agent_config_dir}")
        print(f"[DEBUG] Found YAML files: {[p.name for p in agent_config_dir.glob('*.yaml')]}")
        for agent_file in agent_config_dir.glob('*.yaml'):
            with open(agent_file, "r") as f:
                data = yaml.safe_load(f)
                # If multi-agent YAML, add all top-level keys
                if isinstance(data, dict) and not data.get("name"):
                    for k, v in data.items():
                        registry[k] = v
                else:
                    name = data.get("name")
                    if name:
                        registry[name] = data
        return registry

    def register_test_agents(self):
        """Loads and registers test agent configs."""
        test_configs = self.load_yaml("legion/configs/test_agents.yaml")
        self.agent_configs.update(test_configs)
        for name in test_configs:
            self.agent_channel_ids[name] = self._get_channel_id(name)

    def run_once(self, event=None):
        """Simulates a single orchestrator event loop iteration."""
        if event is None:
            event = {"from": "architect_agent", "content": "hello world"}
        logger.info("Stub run_once called with event: %s", event)
        return self.broadcast(event["content"])

    def run(self, interval: int = 5):
        """Simulates orchestrator main loop."""
        logger.info("Legion orchestrator loop started (interval=%ss).", interval)
        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Legion orchestrator shutdown requested. Exiting loop.")

    @property
    def agent_registry(self):
        """Returns agent configuration registry."""
        # Return a dict of agent_name: agent_obj (here just names)
        return self.agent_configs

    def get_agent_channel(self, agent_name):
        """Returns Discord channel ID for an agent."""
        return self.agent_channel_ids.get(agent_name)

    def ask(self, agent_name, prompt, context=None):
        """Sends a prompt to an agent and returns the response."""
        if agent_name not in self.agent_registry:
            return f"Agent '{agent_name}' not found."
        agent = self.agent_registry[agent_name]
        event = {"from": "user", "content": prompt}
        messages = [
            {"role": "system", "content": agent["system_prompt"]},
            {
                "role": "user",
                "content": agent["user_prompt"].format(
                    event_content=prompt, event=event
                ),
            },
        ]
        if context:
            messages.extend(context)
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        reply = response.choices[0].message.content
        self.memory[agent_name].log_task(
            {"type": "ask", "prompt": prompt, "response": reply}
        )
        return reply

    def broadcast(self, prompt):
        """Broadcasts a prompt to all agents and collects responses."""
        responses = []
        for name in self.agent_registry:
            resp = self.ask(name, prompt)
            responses.append({"agent": name, "response": resp})
        return responses

    def post_update(self, agent_name, content, files=None):
        """Logs an update for an agent."""
        self.memory[agent_name].log_task(
            {"type": "update", "content": content, "files": files or []}
        )
        # Hook: send to Discord channel via integration
        # (to be called by Discord integration)

    def comment_on_post(self, agent_name, target_agent, comment):
        """Logs a comment on another agent's post."""
        self.memory[agent_name].log_task(
            {"type": "comment", "target": target_agent, "comment": comment}
        )
        # Hook: send comment to Discord

    def react_to_post(self, agent_name, target_agent, emoji):
        """Logs a reaction to another agent's post."""
        self.memory[agent_name].log_task(
            {"type": "reaction", "target": target_agent, "emoji": emoji}
        )
        # Hook: send reaction to Discord

    def request_assistance(self, agent_name, issue):
        """Logs a request for assistance."""
        self.memory[agent_name].log_task({"type": "request_assistance", "issue": issue})
        # Hook: notify therapist agent

    def self_assess(self, agent_name):
        """Triggers self-assessment for an agent using recent logs."""
        # Use the agent's self_assessment_prompt and recent logs for assessment
        agent = self.agent_registry[agent_name]
        prompt = agent.get(
            "self_assessment_prompt",
            "Reflect on your recent actions. What went well, what could be improved?",
        )
        logs = self.memory[agent_name].get_task_log()
        # Use last 5 logs for context
        context_logs = logs[-5:] if logs else []
        context_str = "\n".join([str(log) for log in context_logs])
        messages = [
            {"role": "system", "content": agent["system_prompt"]},
            {"role": "user", "content": f"Recent activity:\n{context_str}\n\n{prompt}"},
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        assessment = response.choices[0].message.content
        self.memory[agent_name].log_task(
            {"type": "self_assessment", "summary": assessment}
        )
        return assessment

    def assess_all_agents(self):
        """Triggers self-assessment for all agents."""
        results = {}
        for name in self.agent_registry:
            results[name] = self.self_assess(name)
        return results

    async def periodic_assessments(self, interval_minutes=10):
        """Periodically triggers self-assessment for all agents."""
        while True:
            results = self.assess_all_agents()
            for agent, assessment in results.items():
                # Detect @agent_name mentions
                mentions = re.findall(r"@(\w+)", assessment)
                for mentioned in mentions:
                    self.notify_agent(
                        mentioned,
                        f"Mentioned by {agent} in self-assessment: {assessment[:100]}...",
                    )
            await asyncio.sleep(interval_minutes * 60)

    def notify_agent(self, agent_name, message):
        """Logs a notification for an agent."""
        # Stub: log the notification, could be extended to queue or post to Discord
        logger.info(f"Notify {agent_name}: {message}")

    def send_message(self, from_agent: str, to_agent: str, payload: dict):
        """Sends a message from one agent to another and logs it."""
        payload = dict(payload)  # copy
        payload["from"] = from_agent
        if "timestamp" not in payload:
            payload["timestamp"] = datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()
        logger.info(
            f"Agent {from_agent} → {to_agent}: {payload.get('title', str(payload))}"
        )
        self.memory[from_agent].log_task(
            {"type": "message_sent", "to": to_agent, "payload": payload}
        )
        self.memory[to_agent].log_task(
            {"type": "message_received", "from": from_agent, "payload": payload}
        )
        self.deliver_message(to_agent, payload)

    def deliver_message(self, to_agent: str, payload: dict):
        """Delivers a message to an agent object and logs it."""
        agent_obj = self.agents.get(to_agent)
        if agent_obj and hasattr(agent_obj, "receive_message"):
            logger.info(f"Delivering message to live agent instance: {to_agent}")
            agent_obj.receive_message(payload)
        self.memory[to_agent].log_task({"type": "message_received", "payload": payload})
        logger.info(
            f"Agent {to_agent} not live; message stored in memory: {payload.get('title', str(payload))}"
        )
        # Post to Discord if helper is set
        if self._post_agent_message:
            try:
                fields = [
                    ("From", payload.get("from")),
                    ("To", to_agent),
                    ("Body", payload.get("body")),
                    ("Priority", payload.get("priority", "-")),
                    ("Timestamp", payload.get("timestamp")),
                ]
                embed = render_feed_item(
                    payload.get("from", "?"),
                    payload.get("title", "Message"),
                    fields=fields,
                )
                asyncio.create_task(
                    self._post_agent_message(payload.get("from"), embed)
                )
                embed2 = render_feed_item(
                    to_agent,
                    f"New message from {payload.get('from')}: {payload.get('title')}",
                    fields=fields,
                )
                asyncio.create_task(self._post_agent_message(to_agent, embed2))
            except Exception as e:
                logger.error(f"Failed to post inter-agent message to Discord: {e}")

    def load_yaml(self, path):
        with open(path, "r") as f:
            return yaml.safe_load(f)

    async def dispatch_message(
        self,
        agent_name: str,
        content: str,
        author: str = None,
        timestamp: str = None,
    ):
        """Routes a message to the appropriate agent by name."""
        agent_name = agent_name.lower()
        if agent_name not in self.agents:
            return f"[Error: '{agent_name}' not available. Valid: {', '.join(self.agents.keys())}]"
        agent = self.agents[agent_name]
        return await agent.handle_message(content, author=author, timestamp=timestamp)

    async def run_self_assess_all(self):
        """Run self_assess() on all agents, logging exceptions."""
        for name, agent in self.agents.items():
            if hasattr(agent, "self_assess"):
                try:
                    await agent.self_assess()
                except Exception as e:
                    logger.error(f"[self_assess] Agent {name} failed: {e}")
