import asyncio
import atexit
import datetime
import errno
import fcntl
import json
import logging
import logging.config
import os
import re
import signal
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

import openai
import yaml
import zmq.asyncio
from dotenv import load_dotenv

from integration.discord.cogs.ux_feed import render_feed_item
from legion.agents.python import (
    ArchitectAgent,
    EchoAgent,
    HealthcheckAgent,
    MetricsAgent,
    PingAgent,
    TherapistAgent,
    UxDesignerAgent,
)
from legion.core.di_container import ILLMClient, IStateManager, container
from legion.core.logging_config import setup_logging
from memory.legion_memory import LegionAgentMemory

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
    "ArchitectAgent": ArchitectAgent,
    "MetricsAgent": MetricsAgent,
    "UxDesignerAgent": UxDesignerAgent,
    "TherapistAgent": TherapistAgent,
    "PingAgent": PingAgent,
    "EchoAgent": EchoAgent,
    "HealthcheckAgent": HealthcheckAgent,
}

PID_FILE = "/tmp/legion_orchestrator.pid"

# --- IPC Directories --- START ---
# Define relative to the project root where orchestrator.py is assumed to be
PROJECT_ROOT_ORCH = Path(
    __file__
).parent.parent  # Assuming legion is one level down from root
IPC_DIR_ORCH = PROJECT_ROOT_ORCH / "interface" / "orchestrator_ipc"
COMMAND_DIR_ORCH = IPC_DIR_ORCH / "commands"
RESPONSE_DIR_ORCH = IPC_DIR_ORCH / "responses"
# --- IPC Directories --- END ---


class ProcessRunningError(Exception):
    """Raised when another process is already running."""

    pass


class Orchestrator:
    """Manages agent lifecycle and communication."""

    def __init__(
        self,
        post_agent_message=None,
        pid_file=None,
        state_manager=None,
        llm_client=None,
    ):
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
            # No locking for default startup (e.g., during tests)
            self._pid_file = None

        # Initialize ZeroMQ PUB server for broadcasting task updates
        try:
            self.init_zmq_pub_server("tcp://*:5556")
        except Exception as e:
            logger.error(f"Failed to start ZMQ PUB server: {e}")
        # Initialize ZeroMQ REP server for API commands
        try:
            self.init_zmq_rep_server("tcp://*:5555")
        except Exception as e:
            logger.error(f"Failed to start ZMQ REP server: {e}")

        # Initialize core dependencies (DI)
        self.agents = {}  # Initialize agents dict *before* loading configs
        self.state_manager = state_manager or container.get(IStateManager)
        self.llm_client = llm_client or container.get(ILLMClient)

        self.client = None
        self.task_queue = []
        self.completed_tasks = []

        # Load agent configs first
        self.config = self.load_agent_configs()

        # Populate agent_channel_ids from agent_configs (YAML), fallback to env/channel map
        self.agent_channel_ids = {}
        for name in CLASS_MAP:
            chan = self.config.get(name, {}).get("discord_channel_id")
            if not chan:
                chan = CHANNEL_ID_MAP.get(name, 0)
            self.agent_channel_ids[name] = int(chan) if chan else 0

        # Add new channels to agent_channel_ids for easy access
        self.agent_channel_ids.update(
            {
                "bot_commands": BOT_COMMANDS_CHANNEL_ID,
                "agent_logs": AGENT_LOGS_CHANNEL_ID,
                "agent_feedback": AGENT_FEEDBACK_CHANNEL_ID,
                "config_updates": CONFIG_UPDATES_CHANNEL_ID,
                "alerts": ALERTS_CHANNEL_ID,
                "metrics_dash": METRICS_DASH_CHANNEL_ID,
            }
        )

        self._post_agent_message = post_agent_message or (lambda agent, payload: None)

        # Instantiate agents with validated configs
        for agent_name, config in self.config.items():
            try:
                # Get agent class from CLASS_MAP using class name from config
                agent_class = CLASS_MAP[config["class"]]
                agent = agent_class(
                    orchestrator=self,  # Pass orchestrator instance
                    llm_client=self.llm_client,  # Pass LLM client instance
                )

                # Initialize agent
                if hasattr(agent, "initialize") and callable(agent.initialize):
                    agent.initialize()

                self.agents[agent_name] = agent
                logger.info(f"Loaded agent: {agent_name}")

            except Exception as e:
                logger.error(f"Failed to instantiate agent {agent_name}: {e!s}")
                raise RuntimeError(f"Agent instantiation failed: {e!s}")

        if not self.agents:
            raise RuntimeError("No agents were loaded successfully")

        self.agent_classes = CLASS_MAP
        self.memory = {
            name: LegionAgentMemory(
                name,
                base_dir=self.config.get(name, {}).get("memory_base_dir", "memory"),
            )  # Get base_dir from agent's config
            for name in self.agent_classes
        }

        # Only use self.agents for all agent lookups and dispatches
        for name, agent in self.agents.items():
            agent.config = self.config.get(name, {})
            agent.llm = self.llm_client
            agent.dynamic_rules = agent.config.get("dynamic_rules", {})

        logger.info(
            "Orchestrator initialized with agents: %s", list(self.config.keys())
        )
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
        """Return the Discord channel ID for a given agent name, or the general channel if not found."""
        return CHANNEL_ID_MAP.get(agent_name, GENERAL_CHANNEL_ID)

    def load_agent_configs(self) -> None:
        """
        Load agent configurations from YAML files in the `legion/configs` directory.
        Handles files containing single or multiple agent definitions.

        Also sets orchestrator attributes like self.config and self.agent_channel_ids.

        Raises:
            FileNotFoundError: If config directory or required files missing
            ValueError: If config format is invalid
            RuntimeError: If agent instantiation fails
        """
        config_dir = os.path.join(os.path.dirname(__file__), "configs")
        if not os.path.exists(config_dir):
            raise FileNotFoundError(f"Config directory not found: {config_dir}")

        # Track loaded configs for validation
        loaded_configs = {}
        required_fields = {"name", "class", "prompt", "channel_id"}

        # Files to explicitly skip
        skip_files = ["test_agents.yaml", "discord_channels.yaml", "developer.yaml"]

        # Load and validate each config file
        for filename in os.listdir(config_dir):
            if not filename.endswith(".yaml"):
                continue

            # Skip test-specific or non-agent config files
            if filename in skip_files:
                logger.debug(f"Skipping non-agent config file: {filename}")
                continue

            config_path = os.path.join(config_dir, filename)
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)

                # Check if file contains multiple agent definitions (dictionary)
                if isinstance(config, dict):
                    # Iterate through agent definitions within the file
                    for agent_key, agent_config in config.items():
                        if not isinstance(agent_config, dict):
                            logger.warning(
                                f"Skipping invalid agent definition '{agent_key}' in {filename}: not a dictionary."
                            )
                            continue

                        # Validate required fields for this specific agent
                        missing_fields = required_fields - set(agent_config.keys())
                        if missing_fields:
                            # Log a warning instead of raising error, allows partial loading
                            logger.warning(
                                f"Missing required fields for agent '{agent_key}' in {filename}: {', '.join(missing_fields)}. Skipping this agent."
                            )
                            continue  # Skip this agent definition

                        # Validate agent class exists (if specified)
                        class_name = agent_config.get("class")
                        if not class_name or class_name not in CLASS_MAP:
                            logger.warning(
                                f"Agent '{agent_key}' in {filename} has missing or unknown class '{class_name}'. Skipping."
                            )
                            continue

                        # Store validated config
                        agent_name = agent_config["name"].lower()
                        if agent_name != agent_key.lower():
                            logger.warning(
                                f"Agent key '{agent_key}' does not match name '{agent_name}' in {filename}. Using name field."
                            )

                        if agent_name in loaded_configs:
                            logger.warning(
                                f"Duplicate agent name '{agent_name}' found (from {filename}), overwriting previous definition."
                            )
                        loaded_configs[agent_name] = agent_config

                else:
                    raise ValueError(
                        f"Invalid config format in {filename}: must be a dictionary"
                    )

            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse {filename}: {e!s}")
            except Exception as e:
                raise RuntimeError(f"Error loading {filename}: {e!s}")

        # Store combined config and populate channel IDs
        self.config = loaded_configs
        self.agent_channel_ids = {}
        for agent_name, agent_conf in self.config.items():
            self.agent_channel_ids[agent_name] = int(agent_conf.get("channel_id", 0))

        # Instantiate agents with validated configs
        for agent_name, config in loaded_configs.items():
            try:
                # Get agent class from CLASS_MAP using class name from config
                agent_class = CLASS_MAP[config["class"]]
                agent = agent_class(
                    orchestrator=self,  # Pass orchestrator instance
                    llm_client=self.llm_client,  # Pass LLM client instance
                )

                # Initialize agent
                if hasattr(agent, "initialize") and callable(agent.initialize):
                    agent.initialize()

                self.agents[agent_name] = agent
                logger.info(f"Loaded agent: {agent_name}")

            except Exception as e:
                logger.error(f"Failed to instantiate agent {agent_name}: {e!s}")
                raise RuntimeError(f"Agent instantiation failed: {e!s}")

        if not self.agents:
            raise RuntimeError("No agents were loaded successfully")

    def register_test_agents(self):
        """Register dummy agents for testing."""
        # Implementation needed
        pass

    def run_once(self, event=None):
        """Simulates a single orchestrator event loop iteration."""
        if event is None:
            event = {"from": "architect_agent", "content": "hello world"}
        logger.info("Stub run_once called with event: %s", event)
        return self.broadcast(event["content"])

    def _check_ipc_commands(self):
        """Check for command files from the web interface and process them."""
        processed_files = 0
        if not COMMAND_DIR_ORCH.exists():
            # Directory might not exist on first run or if deleted
            logger.debug("Command directory does not exist, skipping IPC check.")
            return
        try:
            command_files = list(COMMAND_DIR_ORCH.glob("command_*.json"))
            for cmd_file in command_files:
                command_id = None
                response_payload = {
                    "status": "error",
                    "detail": "Unknown processing error",
                }
                try:
                    with open(cmd_file, encoding="utf-8") as f:
                        command_data = json.load(f)

                    command_id = command_data.get("command_id")
                    action = command_data.get("action")
                    payload = command_data.get("payload", {})  # Optional payload

                    logger.info(
                        f"Processing IPC command {command_id} with action '{action}'"
                    )

                    # --- Process supported actions ---
                    if action == "status":
                        # Example: Return basic status
                        response_payload = {
                            "status": "ok",
                            "detail": "Orchestrator is running",
                            "pid": os.getpid(),
                            "active_agents": list(self.agents.keys()),
                        }
                    elif action == "list_agents":
                        response_payload = {
                            "status": "ok",
                            "agents": {
                                name: agent.config
                                for name, agent in self.agents.items()
                            },
                        }
                    elif action == "metrics":
                        # Placeholder: Return basic process metrics or dummy data
                        # In a real implementation, collect actual system/agent metrics
                        response_payload = {
                            "status": "ok",
                            "metrics": {
                                "cpu_usage_percent": 15.5,  # Example
                                "memory_usage_mb": 256.8,  # Example
                                "active_commands": processed_files,  # Example: number of commands processed in this check
                                "pid": os.getpid(),
                            },
                        }
                    elif action == "logs":
                        # Placeholder: Return dummy log entries
                        # In a real implementation, fetch actual logs from logging system or file
                        response_payload = {
                            "status": "ok",
                            "logs": [
                                {
                                    "timestamp": "2023-10-01T10:00:00Z",
                                    "level": "INFO",
                                    "message": "Orchestrator started",
                                    "agent": "system",
                                },
                                {
                                    "timestamp": "2023-10-01T10:01:00Z",
                                    "level": "INFO",
                                    "message": "Agent architect_agent initialized",
                                    "agent": "architect_agent",
                                },
                                {
                                    "timestamp": "2023-10-01T10:02:00Z",
                                    "level": "ERROR",
                                    "message": "Failed to process message",
                                    "agent": "metrics_agent",
                                },
                            ],
                        }
                    else:
                        response_payload = {
                            "status": "error",
                            "detail": f"Unsupported action: {action}",
                        }
                        logger.warning(
                            f"Unsupported IPC action '{action}' in command {command_id}"
                        )

                except (OSError, json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error processing command file {cmd_file.name}: {e}")
                    response_payload = {
                        "status": "error",
                        "detail": f"Error processing command: {e}",
                    }
                except Exception as e:
                    logger.exception(
                        f"Unexpected error processing command {command_id} from {cmd_file.name}"
                    )
                    response_payload = {
                        "status": "error",
                        "detail": f"Unexpected error: {e}",
                    }
                finally:
                    # --- Write response ---
                    if command_id:
                        response_file = (
                            RESPONSE_DIR_ORCH / f"response_{command_id}.json"
                        )
                        temp_response_file = response_file.with_suffix(".tmp")
                        final_payload = {
                            "command_id": command_id,
                            "response": response_payload,
                        }
                        try:
                            with open(temp_response_file, "w", encoding="utf-8") as f:
                                json.dump(final_payload, f, indent=2)
                            os.rename(temp_response_file, response_file)
                        except OSError as e:
                            logger.error(
                                f"Failed to write response file for {command_id}: {e}"
                            )
                            if temp_response_file.exists():
                                os.remove(temp_response_file)

                    # --- Cleanup command file ---
                    try:
                        os.remove(cmd_file)
                        processed_files += 1
                    except OSError as e:
                        logger.warning(f"Could not remove command file {cmd_file}: {e}")

            if processed_files > 0:
                logger.info(f"Processed {processed_files} IPC command(s).")

        except Exception:
            logger.exception("Error occurred while checking IPC commands")

    def run(self, interval: int = 5):
        """Main orchestrator loop. Now relies on ZMQ REP server for commands."""
        logger.info("Starting orchestrator run loop (ZMQ REP active)...")
        if self._pid_file and not self._lock_acquired:
            logger.error("Lock not acquired, cannot start run loop.")
            return

        try:
            while True:
                start_time = time.time()
                # --- Legacy IPC Check - REMOVE LATER --- START ---
                # try:
                #     self._check_ipc_commands()
                # except Exception:
                #     logger.exception("Ignoring error during IPC check to allow loop continuation.")
                # --- Legacy IPC Check - REMOVE LATER --- END ---

                # Core orchestrator logic (agent checks, scheduled tasks) can go here
                # ...

                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                logger.debug(
                    f"Orchestrator idle loop finished in {elapsed:.2f}s. Sleeping for {sleep_time:.2f}s."
                )
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, shutting down orchestrator loop.")
        finally:
            if self._pid_file:
                self._release_lock()
            # Clean up ZMQ socket if it exists
            if hasattr(self, "_zmq_socket") and self._zmq_socket:
                try:
                    self._zmq_socket.close()
                    logger.info("Closed ZMQ REP socket.")
                except Exception as e_close:
                    logger.error(f"Error closing ZMQ socket: {e_close}")

    @property
    def agent_registry(self):
        """Returns agent configuration registry."""
        # Return a dict of agent_name: agent_obj (here just names)
        return self.config

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
                logger.error(
                    f"Failed to post inter-agent message to Discord due to runtime error: {e}"
                )
            except AttributeError as e:
                logger.error(
                    f"Failed to post inter-agent message to Discord due to attribute error: {e}"
                )

    def load_yaml(self, path):
        with open(path) as f:
            return yaml.safe_load(f)

    async def dispatch_message(
        self,
        agent_name: str,
        content: str,
        author: str = None,
        timestamp: str = None,
    ) -> str:
        """
        Dispatch a message to an agent and return its response.

        Args:
            agent_name: Name of the target agent
            content: Message content
            author: Optional message author
            timestamp: Optional message timestamp

        Returns:
            str: Agent's response or error message

        Raises:
            ValueError: If agent_name is invalid
            RuntimeError: If agent dispatch fails
        """
        start_time = time.time()

        # Input validation
        if not agent_name or not content:
            error_msg = (
                "Missing required fields: agent_name and content must be provided"
            )
            logger.error(error_msg)
            return f"Error: {error_msg}"

        if agent_name not in self.agents:
            error_msg = f"Unknown agent: {agent_name}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

        agent = self.agents[agent_name]

        # Structured logging of dispatch event
        dispatch_event = {
            "event": "message_dispatch",
            "agent": agent_name,
            "author": author or "unknown",
            "timestamp": timestamp or datetime.datetime.now().isoformat(),
            "content_length": len(content),
        }
        logger.info("Dispatching message", extra=dispatch_event)

        try:
            # Pre-dispatch validation
            if hasattr(agent, "validate_request"):
                is_valid, reason = await agent.validate_request(content)
                if not is_valid:
                    logger.warning(
                        f"Request validation failed: {reason}",
                        extra={"agent": agent_name, "reason": reason},
                    )
                    return f"Cannot process request: {reason}"

            # Dispatch to agent
            response = await agent.handle_message(
                content, author=author, timestamp=timestamp
            )

            # Post-process response
            if not response or not isinstance(response, str):
                error_msg = f"Invalid response from {agent_name}: {type(response)}"
                logger.error(error_msg)
                return "Error: Agent returned invalid response"

            # Log success metrics
            duration = time.time() - start_time
            self.state_manager.log_telemetry(
                {
                    "event": "message_dispatch_complete",
                    "agent": agent_name,
                    "duration": duration,
                    "status": "success",
                    "response_length": len(response),
                }
            )

            return response

        except Exception as e:
            error_msg = f"Error dispatching message to {agent_name}: {e!s}"
            logger.exception(error_msg)

            # Log failure metrics
            duration = time.time() - start_time
            self.state_manager.log_telemetry(
                {
                    "event": "message_dispatch_complete",
                    "agent": agent_name,
                    "duration": duration,
                    "status": "error",
                    "error": str(e),
                }
            )

            # Notify subscribers of critical errors
            if isinstance(e, (RuntimeError, ValueError)):
                for subscriber in self.alert_subscribers:
                    self.notify_agent(
                        "system", f"Critical error in {agent_name}: {e!s}"
                    )

            return f"Error processing message: {e!s}"

    async def run_self_assess_all(self):
        """Run self_assess() on all agents, logging exceptions."""
        for name, agent in self.agents.items():
            if hasattr(agent, "self_assess"):
                try:
                    await agent.self_assess()
                except RuntimeError as e:
                    logger.error(
                        f"[self_assess] Agent {name} failed due to runtime error: {e}"
                    )
                except AttributeError as e:
                    logger.error(
                        f"[self_assess] Agent {name} failed due to attribute error: {e}"
                    )

    def reload_agent_configs(self, llm_client=None):
        """Reloads agent configurations from YAML files and updates all agents."""
        # Reload configs
        self.config = self.load_agent_configs()
        # Warn and remove unknown config keys
        for key in list(self.config):
            if key not in CLASS_MAP:
                logger.warning(f"Ignoring unknown config key: {key}")
                self.config.pop(key)
        # Optionally reload test agents if present
        test_agents_path = Path(__file__).parent / "configs" / "test_agents.yaml"
        if test_agents_path.exists():
            test_configs = self.load_yaml(str(test_agents_path))
            self.config.update(test_configs)
        # Update channel IDs
        for name in self.config.keys():
            chan = self.config.get(name, {}).get("discord_channel_id")
            if not chan:
                chan = CHANNEL_ID_MAP.get(name, 0)
            self.agent_channel_ids[name] = int(chan) if chan else 0
        # Re-instantiate agents
        self.agents = {
            name: CLASS_MAP[name](self)
            for name in self.config.keys()
            if name in CLASS_MAP
        }
        self._agent_objects = self.agents  # Backward compatibility
        # Update agent attributes
        for name, agent in self.agents.items():
            agent.config = self.config.get(name, {})
            agent.llm = llm_client or container.get(ILLMClient)
            agent.dynamic_rules = agent.config.get("dynamic_rules", {})
        logger.info("Agent configs reloaded. Agents: %s", list(self.config.keys()))

    def submit_feedback(self, feedback: dict) -> None:
        """
        Submit user or audit feedback into the central state store.
        Args:
            feedback (dict): Feedback entry with keys like 'type', 'agent', 'content', 'note'.
        """
        # Store feedback
        self.state_manager.add_feedback(feedback)
        # Example dynamic adjustment: lower threshold on false-positive feedback
        if feedback.get("type") == "validation_false_positive":
            cfg = self.state_manager.get_state()["config"]
            current = cfg.get("confidence_threshold", 0.5)
            new_thresh = max(0.1, current - 0.05)
            self.state_manager.adjust_confidence_threshold(new_thresh)

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
        if agent_name not in self.config:
            raise ValueError(f"Agent '{agent_name}' not found.")
        cfg = self.config[agent_name]
        cfg["model"] = model
        cfg["temperature"] = temperature
        cfg["max_tokens"] = max_tokens
        # Update live agent object
        agent = self.agents[agent_name]
        agent.config = cfg
        agent.llm.model = model
        # Optionally update other attributes as needed
        self.state_manager.log_task(
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
        return self.state_manager.get_state().get(key, None)

    def add_alert_subscriber(self, user_id: int) -> None:
        """Add a user to the alert subscription list."""
        self.alert_subscribers.add(user_id)

    def get_alert_subscribers(self) -> set:
        """Return the set of alert subscriber user IDs."""
        return self.alert_subscribers

    def init_zmq_rep_server(self, bind_address: str) -> None:
        """Initialize ZeroMQ REP socket and start listening for API commands."""
        context = zmq.asyncio.Context.instance()
        self._zmq_socket = context.socket(zmq.REP)
        self._zmq_socket.bind(bind_address)
        logger.info(f"ZeroMQ REP server bound to {bind_address}")
        # Start asyncio loop for handling requests
        asyncio.create_task(self._zmq_rep_loop())

    def init_zmq_pub_server(self, bind_address: str) -> None:
        """Initialize ZeroMQ PUB socket for broadcasting task update events."""
        context = zmq.asyncio.Context.instance()
        self._zmq_pub_socket = context.socket(zmq.PUB)
        self._zmq_pub_socket.bind(bind_address)
        logger.info(f"ZeroMQ PUB server bound to {bind_address}")

    async def _zmq_rep_loop(self):
        """Loop to receive and respond to ZeroMQ REP requests."""
        while True:
            try:
                command = await self._zmq_socket.recv_json()
                request_id = command.get("request_id", "N/A")
                logger.info(
                    f"Received ZMQ command (ID: {request_id}): {command.get('action')}"
                )
                response = self.dispatch_command(command)
                # Include request ID in response for correlation
                if request_id != "N/A":
                    response["request_id"] = request_id
                await self._zmq_socket.send_json(response)
                logger.info(
                    f"Sent ZMQ response (ID: {request_id}) for action: {command.get('action')}"
                )
            except zmq.ZMQError as e:
                logger.error(f"ZMQ communication error in REP loop: {e}")
                # Attempt to send generic error response if possible
                try:
                    await self._zmq_socket.send_json(
                        {"status": "error", "detail": f"ZMQ Error: {e}"}
                    )
                except Exception:
                    pass  # Ignore if sending fails too
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode ZMQ request JSON: {e}")
                await self._zmq_socket.send_json(
                    {"status": "error", "detail": f"Invalid JSON received: {e}"}
                )
            except Exception as e:
                logger.exception(f"Unexpected error in ZMQ REP loop: {e}")
                # Attempt to send a generic error response
                try:
                    await self._zmq_socket.send_json(
                        {
                            "status": "error",
                            "detail": f"Internal orchestrator error: {e}",
                        }
                    )
                except Exception:
                    pass  # Ignore if sending fails

    def dispatch_command(self, command: dict) -> dict:
        """Dispatch incoming command based on 'action' field and return response."""
        action = command.get("action")
        payload = command.get("payload", {})
        try:
            if action == "status":
                return {"status": "success", **self.get_system_status()}
            elif action == "list_agents":
                return {"status": "success", "agents": self.get_agent_list()}
            elif action == "get_agent_status":
                agent_name = payload.get("agent_name")
                if not agent_name:
                    return {
                        "status": "error",
                        "detail": "Missing agent_name in payload",
                    }
                status_info = self.get_agent_status(agent_name)
                if status_info:
                    return {"status": "success", "agent": status_info}
                else:
                    return {
                        "status": "error",
                        "detail": f"Agent '{agent_name}' not found or status unavailable",
                    }
            elif action == "get_agent_config":
                agent_name = payload.get("agent_name")
                if not agent_name:
                    return {
                        "status": "error",
                        "detail": "Missing agent_name in payload",
                    }
                config_info = self.get_agent_config_info(agent_name)
                if config_info:
                    return {"status": "success", "config": config_info}
                else:
                    return {
                        "status": "error",
                        "detail": f"Agent '{agent_name}' not found or config unavailable",
                    }
            elif action == "metrics":
                return {"status": "success", **self.get_system_metrics()}
            elif action == "logs":
                # Placeholder - Requires actual log fetching logic
                return {"status": "success", "logs": self.get_dummy_logs()}
            elif action == "memory_stats":
                return {"status": "success", **self.get_memory_system_stats()}
            elif action == "memory_list_documents":
                docs = (
                    self.state_manager.list_documents()
                )  # Assuming state manager handles this
                return {"status": "success", "documents": docs}
            elif action == "memory_get_document":
                doc_name = payload.get("document_name")
                version = payload.get("version")
                if not doc_name:
                    return {
                        "status": "error",
                        "detail": "Missing document_name in payload",
                    }
                doc_content = self.state_manager.get_document(doc_name, version)
                if doc_content is not None:
                    # Assuming get_document returns content and actual version
                    # Adapt based on actual StateManager implementation
                    return {
                        "status": "success",
                        "name": doc_name,
                        "content": doc_content,
                        "version": version or "latest",
                    }
                else:
                    return {
                        "status": "not_found",
                        "detail": f"Document '{doc_name}' (Version: {version or 'latest'}) not found",
                    }
            elif action == "memory_search_agent":
                # Requires integration with memory search
                agent_name = payload.get("agent_name")
                query = payload.get("query")
                top_k = payload.get("top_k", 5)
                if not agent_name or not query:
                    return {"status": "error", "detail": "Missing agent_name or query"}
                # results = self.memory[agent_name].search(query, top_k)
                results = []  # Placeholder
                return {
                    "status": "success",
                    "results": results,
                    "query": query,
                    "agent_name": agent_name,
                }
            elif action == "memory_search_global":
                # Requires integration with global memory search
                query = payload.get("query")
                top_k = payload.get("top_k", 5)
                if not query:
                    return {"status": "error", "detail": "Missing query"}
                # results = self.search_all_memories(query, top_k)
                results = []  # Placeholder
                return {"status": "success", "results": results, "query": query}

            # --- Task Management Actions ---
            elif action == "create_task":
                task_id = self.create_new_task(payload)  # Needs implementation
                if task_id:
                    # Publish task creation event
                    try:
                        self._zmq_pub_socket.send_json(
                            {
                                "type": "task_created",
                                "task_id": str(task_id),
                                "payload": payload,
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to publish task_created event: {e}")
                    return {"status": "success", "task_id": str(task_id)}
                else:
                    return {"status": "error", "detail": "Failed to create task"}
            elif action == "get_task_status":
                task_id_str = payload.get("task_id")
                if not task_id_str:
                    return {"status": "error", "detail": "Missing task_id"}
                task_info = self.get_task_details(
                    uuid.UUID(task_id_str)
                )  # Needs implementation
                if task_info:
                    return {"status": "success", "task": task_info}
                else:
                    return {
                        "status": "error",
                        "detail": f"Task '{task_id_str}' not found",
                    }
            elif action == "list_tasks":
                tasks, total = self.get_task_list(payload)  # Needs implementation
                return {"status": "success", "tasks": tasks, "total": total}
            elif action == "cancel_task":
                task_id_str = payload.get("task_id")
                if not task_id_str:
                    return {"status": "error", "detail": "Missing task_id"}
                success = self.request_task_cancellation(
                    uuid.UUID(task_id_str)
                )  # Needs implementation
                if success:
                    # Publish task cancellation event
                    try:
                        self._zmq_pub_socket.send_json(
                            {"type": "task_cancelled", "task_id": task_id_str}
                        )
                    except Exception as e:
                        logger.error(f"Failed to publish task_cancelled event: {e}")
                    return {"status": "success"}
                else:
                    return {
                        "status": "error",
                        "detail": f"Failed to cancel task '{task_id_str}'",
                    }

            # --- Agent Lifecycle Actions ---
            elif action == "start_agent":
                agent_name = payload.get("agent_name")
                if not agent_name:
                    return {
                        "status": "error",
                        "detail": "Missing agent_name in payload",
                    }
                success, detail = self.start_agent(agent_name)  # Needs implementation
                return {"status": "success" if success else "error", "detail": detail}
            elif action == "stop_agent":
                agent_name = payload.get("agent_name")
                if not agent_name:
                    return {
                        "status": "error",
                        "detail": "Missing agent_name in payload",
                    }
                success, detail = self.stop_agent(agent_name)  # Needs implementation
                return {"status": "success" if success else "error", "detail": detail}
            elif action == "restart_agent":
                agent_name = payload.get("agent_name")
                if not agent_name:
                    return {
                        "status": "error",
                        "detail": "Missing agent_name in payload",
                    }
                success, detail = self.restart_agent(agent_name)  # Needs implementation
                return {"status": "success" if success else "error", "detail": detail}

            # --- Reload Config Action ---
            elif action == "reload_agent_configs":
                logger.info("Reloading agent configurations via ZMQ request...")
                # Note: self.reload_agent_configs might need the llm_client if not already available
                # Assuming llm_client is accessible via self.llm or similar attribute set during init
                try:
                    self.reload_agent_configs(
                        llm_client=self.llm_client
                    )  # Pass necessary dependencies if needed
                    return {
                        "status": "success",
                        "detail": "Agent configurations reloaded successfully.",
                    }
                except Exception as e:
                    logger.exception("Error during agent config reload.")
                    return {
                        "status": "error",
                        "detail": f"Failed to reload agent configurations: {e!s}",
                    }

            # --- Default ---
            else:
                logger.warning(f"Received unsupported ZMQ action: {action}")
                return {"status": "error", "detail": f"Unsupported action: {action}"}
        except Exception as e:
            logger.exception(f"Error processing ZMQ action '{action}': {e}")
            return {"status": "error", "detail": str(e)}

    # --- Helper methods for ZMQ dispatch ---
    def get_system_status(self) -> dict:
        # Replicate logic from old _check_ipc_commands or enhance
        return {
            "detail": "Orchestrator is running",
            "pid": os.getpid(),
            "active_agents": list(self.agents.keys()),
        }

    def get_agent_list(self) -> list:
        # Format similar to API response expectation
        agent_list = []
        for name, agent in self.agents.items():
            # Add more status details if available
            agent_list.append(
                {"name": name, "status": "unknown", "config": agent.config}
            )
        return agent_list

    def get_agent_status(self, agent_name: str) -> Optional[dict]:
        # Needs to query actual agent status (e.g., via agent object or state)
        agent = self.agents.get(agent_name)
        if agent:
            # Placeholder - fetch real status
            return {
                "name": agent_name,
                "status": "running",  # Dummy
                "tasks": 0,  # Dummy
                "config": agent.config,  # Include config for detail
            }
        return None

    def get_agent_config_info(self, agent_name: str) -> Optional[dict]:
        agent = self.agents.get(agent_name)
        return agent.config if agent else None

    def get_system_metrics(self) -> dict:
        # Placeholder - fetch real metrics
        return {
            "metrics": {
                "cpu_usage_percent": 0.0,
                "memory_usage_mb": 0.0,
                "pid": os.getpid(),
            }
        }

    def get_dummy_logs(self) -> list:
        # Placeholder
        return [
            {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "level": "INFO",
                "message": "Log fetching via ZMQ active.",
                "agent": "system",
            }
        ]

    def get_memory_system_stats(self) -> dict:
        # Placeholder - Requires StateManager integration
        return {
            "memory_stats": {
                "vector_db_size_gb": 0.0,
                "sql_db_size_mb": 0.0,
            }
        }

    # --- Placeholder Task Management Methods ---
    def create_new_task(self, payload: dict) -> Optional[uuid.UUID]:
        # TODO: Implement task creation logic (e.g., add to queue, update state)
        logger.info(f"Placeholder: Creating task with payload: {payload}")
        new_id = uuid.uuid4()
        # self.state_manager.log_task({...}) # Persist task
        return new_id

    def get_task_details(self, task_id: uuid.UUID) -> Optional[dict]:
        # TODO: Fetch task details from StateManager or task queue
        logger.info(f"Placeholder: Fetching task details for {task_id}")
        # task_data = self.state_manager.get_task(task_id)
        # return task_data if task_data else None
        return {
            "id": str(task_id),
            "status": "pending",
            "title": "Dummy Task",
        }  # Dummy response

    def get_task_list(self, filters: dict) -> (list, int):
        # TODO: Fetch task list from StateManager with filters
        logger.info(f"Placeholder: Listing tasks with filters: {filters}")
        # tasks, total = self.state_manager.list_tasks(**filters)
        # return tasks, total
        dummy_task = {
            "id": str(uuid.uuid4()),
            "status": "pending",
            "title": "Dummy Task",
        }
        return [dummy_task], 1  # Dummy response

    def request_task_cancellation(self, task_id: uuid.UUID) -> bool:
        # TODO: Send cancellation request (e.g., update status, signal worker)
        logger.info(f"Placeholder: Requesting cancellation for task {task_id}")
        # success = self.state_manager.update_task_status(task_id, "cancelled")
        # return success
        return True  # Dummy response

    # --- Placeholder Agent Lifecycle Methods ---
    def start_agent(self, agent_name: str) -> tuple[bool, str]:
        """Placeholder: Start the specified agent."""
        if agent_name not in self.agents:
            return False, f"Agent '{agent_name}' not found."
        logger.info(f"Placeholder: Starting agent '{agent_name}'...")
        # TODO: Implement actual agent start logic (e.g., process creation, state update)
        return True, f"Agent '{agent_name}' started successfully (Placeholder)."

    def stop_agent(self, agent_name: str) -> tuple[bool, str]:
        """Placeholder: Stop the specified agent."""
        if agent_name not in self.agents:
            return False, f"Agent '{agent_name}' not found."
        logger.info(f"Placeholder: Stopping agent '{agent_name}'...")
        # TODO: Implement actual agent stop logic (e.g., signal process, state update)
        return True, f"Agent '{agent_name}' stopped successfully (Placeholder)."

    def restart_agent(self, agent_name: str) -> tuple[bool, str]:
        """Placeholder: Restart the specified agent."""
        if agent_name not in self.agents:
            return False, f"Agent '{agent_name}' not found."
        logger.info(f"Placeholder: Restarting agent '{agent_name}'...")
        # TODO: Implement actual agent restart logic (stop then start)
        stop_success, stop_detail = self.stop_agent(agent_name)
        if not stop_success:
            return False, f"Failed to stop agent during restart: {stop_detail}"
        start_success, start_detail = self.start_agent(agent_name)
        if not start_success:
            return False, f"Failed to start agent during restart: {start_detail}"
        return True, f"Agent '{agent_name}' restarted successfully (Placeholder)."


# Allow direct execution to start the orchestrator loop
if __name__ == "__main__":
    # Ensure logging is set up before creating Orchestrator instance
    setup_logging()
    orch = Orchestrator(
        pid_file=PID_FILE,
        state_manager=container.get(IStateManager),
        llm_client=container.get(ILLMClient),
    )
    try:
        orch.run()
    except KeyboardInterrupt:
        pass
