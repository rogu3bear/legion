import logging
import logging.config
import os
import time
import fcntl
import errno
import atexit
import signal
import sys
from pathlib import Path
import asyncio
import datetime
import re

import openai
import yaml
from dotenv import load_dotenv

from memory.legion_memory import LegionAgentMemory
from legion.core.llm_client import LLMClient
from legion.core.state import StateManager
from legion.agents.python import (
    ArchitectAgent,
    MetricsAgent,
    UxDesignerAgent,
    TherapistAgent,
    PingAgent,
    EchoAgent,
    HealthcheckAgent,
)
from legion.core.indexing import render_feed_item
from legion.core.di_container import container, IStateManager, ILLMClient
from legion.core.logging_config import setup_logging

# Setup structured logging early
setup_logging()

logging.getLogger("openai").setLevel(logging.ERROR)
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
BOT_COMMANDS_CHANNEL_ID = int(os.getenv("BOT_COMMANDS_CHANNEL_ID", "0"))
AGENT_LOGS_CHANNEL_ID = int(os.getenv("AGENT_LOGS_CHANNEL_ID", "0"))
AGENT_FEEDBACK_CHANNEL_ID = int(os.getenv("AGENT_FEEDBACK_CHANNEL_ID", "0"))
CONFIG_UPDATES_CHANNEL_ID = int(os.getenv("CONFIG_UPDATES_CHANNEL_ID", "0"))
ALERTS_CHANNEL_ID = int(os.getenv("ALERTS_CHANNEL_ID", "0"))
METRICS_DASH_CHANNEL_ID = int(os.getenv("METRICS_DASH_CHANNEL_ID", "0"))

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
    # New channels
    "bot_commands": BOT_COMMANDS_CHANNEL_ID,
    "agent_logs": AGENT_LOGS_CHANNEL_ID,
    "agent_feedback": AGENT_FEEDBACK_CHANNEL_ID,
    "config_updates": CONFIG_UPDATES_CHANNEL_ID,
    "alerts": ALERTS_CHANNEL_ID,
    "metrics_dash": METRICS_DASH_CHANNEL_ID,
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

class ProcessRunningError(Exception):
    """Raised when another process is already running."""
    pass

class Orchestrator:
    """Manages agent lifecycle and communication."""

    def __init__(self, post_agent_message=None, pid_file=None, state_manager=None, llm_client=None):
        # Only enforce locking when a pid_file is explicitly provided
        self._lock_fd = None
        self._lock_acquired = False
        if pid_file is not None:
            self._pid_file = pid_file
            # Duplicate startup check with proper file locking
            try:
                self._acquire_lock()
            except ProcessRunningError as e:
                logger.error(f"Another orchestrator is already running: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Failed to acquire lock: {e}")
                sys.exit(1)
            # Set up graceful shutdown handlers
            self._setup_signal_handlers()
        else:
            # No locking for default startup (e.g., during tests or simple runs)
            self._pid_file = None

        # Populate agent_channel_ids from agent_configs (YAML), fallback to env/channel map
        self.agent_channel_ids = {}
        for name in CLASS_MAP.keys():
            config = self.load_agent_configs().get(name, {})
            chan = config.get('discord_channel_id')
            if not chan:
                chan = CHANNEL_ID_MAP.get(name, 0)
            self.agent_channel_ids[name] = int(chan) if chan else 0

        # Add new channels to agent_channel_ids for easy access
        self.agent_channel_ids.update({
            'bot_commands': BOT_COMMANDS_CHANNEL_ID,
            'agent_logs': AGENT_LOGS_CHANNEL_ID,
            'agent_feedback': AGENT_FEEDBACK_CHANNEL_ID,
            'config_updates': CONFIG_UPDATES_CHANNEL_ID,
            'alerts': ALERTS_CHANNEL_ID,
            'metrics_dash': METRICS_DASH_CHANNEL_ID,
        })

        self._post_agent_message = post_agent_message or (lambda agent, payload: None)

        # Load agent configs and instantiate agents
        self.agent_configs = self.load_agent_configs()

        # Warn and remove unknown config keys
        for key in list(self.agent_configs):
            if key not in CLASS_MAP:
                logger.warning(f"Ignoring unknown config key: {key}")
                self.agent_configs.pop(key)

        self.agents = {
            name: CLASS_MAP[name](self)
            for name in self.agent_configs.keys()
            if name in CLASS_MAP
        }
        self._agent_objects = self.agents  # Backward compatibility for legacy tests

        self.agent_classes = CLASS_MAP
        self.memory = {name: LegionAgentMemory(name) for name in self.agent_classes}

        # Only use self.agents for all agent lookups and dispatches
        for name, agent in self.agents.items():
            agent.config = self.agent_configs.get(name, {})
            agent.llm = llm_client or container.get(ILLMClient)
            agent.dynamic_rules = agent.config.get('dynamic_rules', {})

        # Central state repository
        self.state = state_manager or container.get(IStateManager)
        logger.info("Orchestrator initialized with agents: %s", list(self.agent_configs.keys()))
        self.alert_subscribers = set()  # User IDs for alert DMs

    def _acquire_lock(self):
        """Acquire an exclusive lock on the PID file."""
        try:
            # Open the PID file in read/write mode, create if doesn't exist
            self._lock_fd = os.open(self._pid_file, os.O_RDWR | os.O_CREAT, 0o600)

            # Try to acquire an exclusive lock
            fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Get existing PID if any
            try:
                pid_data = os.read(self._lock_fd, 32).decode().strip()
                if pid_data:
                    pid = int(pid_data)
                    # Check if process is running
                    try:
                        os.kill(pid, 0)
                        raise ProcessRunningError(f"Process {pid} is already running")
                    except OSError as e:
                        if e.errno == errno.ESRCH:  # No such process
                            logger.info(f"Removing stale PID {pid}")
                        else:
                            raise
            except (ValueError, UnicodeDecodeError) as e:
                logger.info(f"Corrupt PID file, will overwrite: {e}")

            # Write our PID
            os.ftruncate(self._lock_fd, 0)
            os.lseek(self._lock_fd, 0, os.SEEK_SET)
            os.write(self._lock_fd, str(os.getpid()).encode())

            self._lock_acquired = True
            atexit.register(self._release_lock)
            logger.info(f"Acquired orchestrator lock (PID {os.getpid()})")

        except BlockingIOError as e:
            raise ProcessRunningError(f"Another process holds the lock: {e}")
        except OSError as e:
            if self._lock_fd is not None:
                try:
                    os.close(self._lock_fd)
                except OSError:
                    pass
            raise RuntimeError(f"Failed to acquire lock due to OS error: {e}")

    def _release_lock(self):
        """Release the lock and clean up the PID file."""
        if self._lock_acquired and self._lock_fd is not None:
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                os.close(self._lock_fd)
                os.unlink(self._pid_file)
                logger.info("Released orchestrator lock and cleaned up PID file")
            except OSError as e:
                logger.error(f"Failed to release lock due to OS error: {e}")
            except FileNotFoundError as e:
                logger.error(f"Failed to release lock due to missing PID file: {e}")
        self._lock_acquired = False
        self._lock_fd = None

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
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
        config_path = os.getenv("ORCH_CONFIG_PATH")
        if config_path:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict) and not data.get("name"):
                    for k, v in data.items():
                        registry[k] = v
                else:
                    name = data.get("name")
                    if name:
                        registry[name] = data
            return registry
        agent_config_dir = Path(__file__).parent / "configs"
        print(f"[DEBUG] Scanning agent config dir: {agent_config_dir}")
        print(
            f"[DEBUG] Found YAML files: {[p.name for p in agent_config_dir.glob('*.yaml')]}"
        )
        for agent_file in agent_config_dir.glob("*.yaml"):
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
                try:
                    self.run_once()
                except Exception as e:
                    logger.error(f"Error during orchestrator loop iteration: {e}", exc_info=True)
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
        try:
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
        except Exception as e:
            logger.error(f"Unexpected error in ask('{agent_name}'): {e}", exc_info=True)
            return "[Error: Agent request failed]"

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
            except RuntimeError as e:
                logger.error(f"Failed to post inter-agent message to Discord due to runtime error: {e}")
            except AttributeError as e:
                logger.error(f"Failed to post inter-agent message to Discord due to attribute error: {e}")

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
        """Routes a message to the appropriate agent by name, with validation."""
        import time
        start_time = time.time()
        try:
            agent_name = agent_name.lower()
            if agent_name not in self.agents:
                return f"[Error: '{agent_name}' not available. Valid: {', '.join(self.agents.keys())}]"
            agent = self.agents[agent_name]
            # Log dispatch event
            self.state.log_task(
                {
                    "type": "dispatch",
                    "agent": agent_name,
                    "content": content,
                    "author": author,
                    "timestamp": timestamp,
                }
            )
            # Build context for validation
            context = {
                "author": author,
                "timestamp": timestamp,
                "content": content,
            }
            # If agent has validate_request, use it
            if hasattr(agent, "validate_request") and callable(
                getattr(agent, "validate_request")
            ):
                # use threshold from state.config
                self.state.get_state()["config"].get("confidence_threshold", 0.5)
                is_valid = agent.validate_request(content, context)
                if not is_valid:
                    # Log validation failure
                    self.state.log_error(
                        {
                            "type": "validation_failed",
                            "agent": agent_name,
                            "content": content,
                            "reason": "validate_request returned False",
                            "timestamp": timestamp,
                        }
                    )
                    if hasattr(agent, "fallback_response") and callable(
                        getattr(agent, "fallback_response")
                    ):
                        fallback = agent.fallback_response(
                            "Request not recognized as valid or confidence too low."
                        )
                        # Optionally post to Discord if agent has post_to_discord
                        if hasattr(agent, "post_to_discord") and callable(
                            getattr(agent, "post_to_discord")
                        ):
                            await agent.post_to_discord(fallback)
                        # Log fallback response
                        self.state.log_task(
                            {
                                "type": "fallback",
                                "agent": agent_name,
                                "response": fallback,
                                "timestamp": timestamp,
                            }
                        )
                        # Record false-positive feedback for validation
                        self.state.add_feedback(
                            {
                                "type": "validation_false_positive",
                                "agent": agent_name,
                                "content": content,
                                "note": "Fallback triggered for invalid request",
                            }
                        )
                        return fallback
                    else:
                        return "[Validation failed: request not permitted for this agent.]"
            # Log validation success
            self.state.log_task(
                {
                    "type": "validated",
                    "agent": agent_name,
                    "content": content,
                    "timestamp": timestamp,
                }
            )
            # Route to agent logic
            llm_start = time.time()
            reply = await agent.handle_message(content, author=author, timestamp=timestamp)
            llm_end = time.time()
            self.state.log_telemetry({
                "type": "llm_latency",
                "agent": agent_name,
                "latency": llm_end - llm_start,
                "event": "handle_message"
            })
            # Post the reply to Discord channel
            try:
                await agent.post_to_discord(reply)
            except Exception as e:
                logger.error(f"Failed to post reply for {agent_name}: {e}")
            # Log response
            self.state.log_task(
                {
                    "type": "response",
                    "agent": agent_name,
                    "response": reply,
                    "timestamp": timestamp,
                }
            )
            dispatch_end = time.time()
            self.state.log_telemetry({
                "type": "dispatch_duration",
                "agent": agent_name,
                "latency": dispatch_end - start_time,
                "event": "dispatch_message"
            })
            return reply
        except Exception as e:
            logger.error(f"Unexpected error in dispatch_message: {e}", exc_info=True)
            return "[Error: Internal error during message dispatch]"

    async def run_self_assess_all(self):
        """Run self_assess() on all agents, logging exceptions."""
        for name, agent in self.agents.items():
            if hasattr(agent, "self_assess"):
                try:
                    await agent.self_assess()
                except RuntimeError as e:
                    logger.error(f"[self_assess] Agent {name} failed due to runtime error: {e}")
                except AttributeError as e:
                    logger.error(f"[self_assess] Agent {name} failed due to attribute error: {e}")

    def reload_agent_configs(self, llm_client=None):
        """Reloads agent configurations from YAML files and updates all agents."""
        # Reload configs
        self.agent_configs = self.load_agent_configs()
        # Warn and remove unknown config keys
        for key in list(self.agent_configs):
            if key not in CLASS_MAP:
                logger.warning(f"Ignoring unknown config key: {key}")
                self.agent_configs.pop(key)
        # Optionally reload test agents if present
        test_agents_path = Path(__file__).parent / "configs" / "test_agents.yaml"
        if test_agents_path.exists():
            test_configs = self.load_yaml(str(test_agents_path))
            self.agent_configs.update(test_configs)
        # Update channel IDs
        for name in self.agent_configs.keys():
            config = self.agent_configs.get(name, {})
            chan = config.get("discord_channel_id")
            if not chan:
                chan = CHANNEL_ID_MAP.get(name, 0)
            self.agent_channel_ids[name] = int(chan) if chan else 0
        # Re-instantiate agents
        self.agents = {
            name: self.agent_classes[name](self)
            for name in self.agent_configs.keys()
            if name in self.agent_classes
        }
        self._agent_objects = self.agents  # Backward compatibility
        # Update agent attributes
        for name, agent in self.agents.items():
            agent.config = self.agent_configs.get(name, {})
            agent.llm = llm_client or container.get(ILLMClient)
            agent.dynamic_rules = agent.config.get("dynamic_rules", {})
        logger.info(
            "Agent configs reloaded. Agents: %s", list(self.agent_configs.keys())
        )

    def submit_feedback(self, feedback: dict) -> None:
        """
        Submit user or audit feedback into the central state store.
        Args:
            feedback (dict): Feedback entry with keys like 'type', 'agent', 'content', 'note'.
        """
        # Store feedback
        self.state.add_feedback(feedback)
        # Example dynamic adjustment: lower threshold on false-positive feedback
        if feedback.get("type") == "validation_false_positive":
            cfg = self.state.get_state()["config"]
            current = cfg.get("confidence_threshold", 0.5)
            new_thresh = max(0.1, current - 0.05)
            self.state.adjust_confidence_threshold(new_thresh)

    def update_agent_config(
        self, agent_name: str, model: str, temperature: float, max_tokens: int
    ) -> None:
        """
        Update the config for a given agent and reload its attributes.
        Args:
            agent_name (str): The agent to update.
            model (str): LLM model name.
            temperature (float): LLM temperature.
            max_tokens (int): LLM max tokens.
        Raises:
            ValueError: If agent_name is not found.
        """
        if agent_name not in self.agent_configs:
            raise ValueError(f"Agent '{agent_name}' not found.")
        cfg = self.agent_configs[agent_name]
        cfg["model"] = model
        cfg["temperature"] = temperature
        cfg["max_tokens"] = max_tokens
        # Update live agent object
        agent = self.agents[agent_name]
        agent.config = cfg
        agent.llm.model = model
        # Optionally update other attributes as needed
        self.state.log_task(
            {
                "type": "config_update",
                "agent": agent_name,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )

    def get_state_key(self, key: str) -> object:
        """
        Return the value for a given key from the central state.
        Args:
            key (str): The state key to query.
        Returns:
            object: The value for the key, or None if not found.
        """
        return self.state.get_state().get(key, None)

    def add_alert_subscriber(self, user_id: int) -> None:
        """Add a user to the alert subscription list."""
        self.alert_subscribers.add(user_id)

    def get_alert_subscribers(self) -> set:
        """Return the set of alert subscriber user IDs."""
        return self.alert_subscribers

# Allow direct execution to start the orchestrator loop
if __name__ == "__main__":
    # Ensure logging is set up before creating Orchestrator instance
    setup_logging()
    orch = Orchestrator(pid_file=PID_FILE, state_manager=container.get(IStateManager), llm_client=container.get(ILLMClient))
    try:
        orch.run()
    except KeyboardInterrupt:
        pass
