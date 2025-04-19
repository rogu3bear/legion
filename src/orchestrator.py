"""
Core orchestrator for Legion agents powered by Microsoft Autogen.
"""
import os
import glob
import yaml
import time
import logging
import logging.config
from src.legion_memory import LegionAgentMemory
from src.indexing import index_documents
from dotenv import load_dotenv
import openai
import asyncio
import re
from src.agents.base_agent import BaseAgent
import importlib
from src.legion_tools import load_yaml

# Configure logging if a YAML config exists
LOGGING_CONFIG_PATH = os.path.join("config", "logging.yaml")
if os.path.exists(LOGGING_CONFIG_PATH):
    with open(LOGGING_CONFIG_PATH, "r") as f:
        logging_config = yaml.safe_load(f)
    logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Only load .env if OpenAI config is used
try:
    load_dotenv(dotenv_path=".env/.env")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_base = os.getenv("OPENAI_API_BASE_URL")
    model = os.getenv("OPENAI_MODEL")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.5))
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 1000))
    top_p = float(os.getenv("OPENAI_TOP_P", 1))
    frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", 0))
    presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", 0))
except ImportError:
    pass

AGENT_CHANNELS = {
    "architect_agent": "architect-channel",
    "metrics_agent": "metrics-channel",
    "therapist_agent": "therapist-channel",
    "ux_designer_agent": "ux-designer-channel"
}

class Orchestrator:
    """Stub orchestrator (AutoGen code removed)."""

    def __init__(self, post_agent_message=None):
        self.memory = {}
        self.agent_configs = self.load_agent_configs()
        self.agent_channel_ids = {name: cfg.get('discord_channel_id') for name, cfg in self.agent_configs.items()}
        self.register_test_agents()
        self._agent_objects = {}
        self._post_agent_message = post_agent_message  # Discord posting helper
        # Update agent_channel_ids after registering test agents
        self.agent_channel_ids = {name: cfg.get('discord_channel_id') for name, cfg in self.agent_configs.items()}
        for name, agent_def in self.agent_configs.items():
            self.memory[name] = LegionAgentMemory(name)
            class_name = ''.join([part.capitalize() for part in name.split('_')])
            try:
                module = importlib.import_module(f"src.agents.{name}")
                agent_cls = getattr(module, class_name)
            except Exception:
                agent_cls = BaseAgent
            self._agent_objects[name] = agent_cls(name)
        logger.info("Orchestrator initialized with agents: %s", list(self.agent_configs.keys()))
        import datetime
        test_payload = {"title": "ping", "body": "hello", "timestamp": datetime.datetime.utcnow().isoformat()}
        self.send_message("architect_agent", "metrics_agent", test_payload)

    def load_agent_configs(self):
        registry = {}
        for agent_file in glob.glob(os.path.join("agent-definitions", "*.yaml")):
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
        test_configs = load_yaml("agent-definitions/test_agents.yaml")
        self.agent_configs.update(test_configs)
        for name, cfg in test_configs.items():
            self.agent_channel_ids[name] = cfg["discord_channel_id"]

    def run_once(self, event=None):
        """Stub run_once (AutoGen code removed). Returns a fake event list."""
        if event is None:
            event = {"from": "architect_agent", "content": "hello world"}
        logger.info("Stub run_once called with event: %s", event)
        return self.broadcast(event["content"])

    def run(self, interval: int = 5):
        """Stub run (AutoGen code removed)."""
        logger.info("Legion orchestrator loop started (interval=%ss).", interval)
        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Legion orchestrator shutdown requested. Exiting loop.")

    @property
    def agent_registry(self):
        # Return a dict of agent_name: agent_obj (here just names)
        return self.agent_configs

    def get_agent_channel(self, agent_name):
        return self.agent_channel_ids.get(agent_name)

    def ask(self, agent_name, prompt, context=None):
        if agent_name not in self.agent_registry:
            return f"Agent '{agent_name}' not found."
        agent = self.agent_registry[agent_name]
        event = {"from": "user", "content": prompt}
        messages = [
            {"role": "system", "content": agent["system_prompt"]},
            {"role": "user",   "content": agent["user_prompt"].format(event_content=prompt, event=event)}
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
            presence_penalty=presence_penalty
        )
        reply = response.choices[0].message.content
        self.memory[agent_name].log_task({"type": "ask", "prompt": prompt, "response": reply})
        return reply

    def broadcast(self, prompt):
        responses = []
        for name in self.agent_registry:
            resp = self.ask(name, prompt)
            responses.append({"agent": name, "response": resp})
        return responses

    def post_update(self, agent_name, content, files=None):
        self.memory[agent_name].log_task({"type": "update", "content": content, "files": files or []})
        # Hook: send to Discord channel via integration
        # (to be called by Discord integration)

    def comment_on_post(self, agent_name, target_agent, comment):
        self.memory[agent_name].log_task({"type": "comment", "target": target_agent, "comment": comment})
        # Hook: send comment to Discord

    def react_to_post(self, agent_name, target_agent, emoji):
        self.memory[agent_name].log_task({"type": "reaction", "target": target_agent, "emoji": emoji})
        # Hook: send reaction to Discord

    def request_assistance(self, agent_name, issue):
        self.memory[agent_name].log_task({"type": "request_assistance", "issue": issue})
        # Hook: notify therapist agent

    def self_assess(self, agent_name):
        # Use the agent's self_assessment_prompt and recent logs for assessment
        agent = self.agent_registry[agent_name]
        prompt = agent.get("self_assessment_prompt", "Reflect on your recent actions. What went well, what could be improved?")
        logs = self.memory[agent_name].get_task_log()
        # Use last 5 logs for context
        context_logs = logs[-5:] if logs else []
        context_str = "\n".join([str(log) for log in context_logs])
        messages = [
            {"role": "system", "content": agent["system_prompt"]},
            {"role": "user", "content": f"Recent activity:\n{context_str}\n\n{prompt}"}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        assessment = response.choices[0].message.content
        self.memory[agent_name].log_task({"type": "self_assessment", "summary": assessment})
        return assessment

    def assess_all_agents(self):
        results = {}
        for name in self.agent_registry:
            results[name] = self.self_assess(name)
        return results

    async def periodic_assessments(self, interval_minutes=10):
        while True:
            results = self.assess_all_agents()
            for agent, assessment in results.items():
                # Detect @agent_name mentions
                mentions = re.findall(r"@(\w+)", assessment)
                for mentioned in mentions:
                    self.notify_agent(mentioned, f"Mentioned by {agent} in self-assessment: {assessment[:100]}...")
            await asyncio.sleep(interval_minutes * 60)

    def notify_agent(self, agent_name, message):
        # Stub: log the notification, could be extended to queue or post to Discord
        logger.info(f"Notify {agent_name}: {message}")

    def send_message(self, from_agent: str, to_agent: str, payload: dict):
        import datetime
        payload = dict(payload)  # copy
        payload['from'] = from_agent
        if 'timestamp' not in payload:
            payload['timestamp'] = datetime.datetime.utcnow().isoformat()
        logger.info(f"Agent {from_agent} → {to_agent}: {payload.get('title', str(payload))}")
        self.memory[from_agent].log_task({"type": "message_sent", "to": to_agent, "payload": payload})
        self.memory[to_agent].log_task({"type": "message_received", "from": from_agent, "payload": payload})
        self.deliver_message(to_agent, payload)

    def deliver_message(self, to_agent: str, payload: dict):
        agent_obj = self._agent_objects.get(to_agent)
        if agent_obj and hasattr(agent_obj, 'receive_message'):
            logger.info(f"Delivering message to live agent instance: {to_agent}")
            agent_obj.receive_message(payload)
        self.memory[to_agent].log_task({"type": "message_received", "payload": payload})
        logger.info(f"Agent {to_agent} not live; message stored in memory: {payload.get('title', str(payload))}")
        # Post to Discord if helper is set
        if self._post_agent_message:
            try:
                from src.ux_feed import render_feed_item
                fields = [
                    ("From", payload.get("from")),
                    ("To", to_agent),
                    ("Body", payload.get("body")),
                    ("Priority", payload.get("priority", "-")),
                    ("Timestamp", payload.get("timestamp")),
                ]
                embed = render_feed_item(payload.get("from", "?"), payload.get("title", "Message"), fields=fields)
                asyncio.create_task(self._post_agent_message(payload.get("from"), embed))
                embed2 = render_feed_item(to_agent, f"New message from {payload.get('from')}: {payload.get('title')}", fields=fields)
                asyncio.create_task(self._post_agent_message(to_agent, embed2))
            except Exception as e:
                logger.error(f"Failed to post inter-agent message to Discord: {e}")
