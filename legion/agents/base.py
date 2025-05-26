"""
Base agent class for Legion agents.

Provides core agent logic, Discord posting, memory, and LLM integration.
"""

import contextlib
import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import openai
import asyncio
import json
import redis
import html # For unescaping

from core.di_container import ILLMClient, container
from core.logging_config import setup_logging
from core.prompt_builder import PromptBuilder
from memory.legion_memory import LegionAgentMemory

logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

AGENT_EMOJIS = {
    "architect_agent": "🏗️",
    "metrics_agent": "📊",
    "ux_designer_agent": "🎨",
    "therapist_agent": "🗣️",
    "ping_agent": "📶",
    "echo_agent": "🔁",
    "healthcheck_agent": "✅",
}


class BaseAgent:
    """Base class for all Legion agents, providing shared logic and interfaces."""

    def __init__(
        self,
        name: str,
        config: dict,
        llm_client: "ILLMClient" = None,
        state_manager: "IStateManager" = None,
        orchestrator_ref: Optional[Any] = None,
    ):
        """Initialize the Base Agent with dependency injection for LLM client and state manager."""
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"agent.{name}")
        setup_logging()  # Ensure logging is configured
        self.logger.info(f"Agent {name} initialized", extra={"agent_name": name})
        self.orchestrator = orchestrator_ref
        self.client = None
        if self.orchestrator and hasattr(self.orchestrator, "agent_channel_ids"):
            self.channel_id = self.orchestrator.agent_channel_ids.get(self.name, 0)
        else:
            self.channel_id = 0
        self.dynamic_rules = {}
        self.memory = LegionAgentMemory(self.name)
        self.introduced = False
        self._self_assessment_running = False
        self._self_assessment_lock = threading.Lock()
        self.llm = llm_client or container.get(ILLMClient)

        if not hasattr(self, 'system_prompt'):
            self.system_prompt = "You are a helpful assistant."
        if not hasattr(self, 'skills'):
            self.skills = []

        if orchestrator_ref is not None:
            try:
                loop = asyncio.get_running_loop()
                if loop and loop.is_running():
                    asyncio.create_task(self._listen_for_prompt_updates())
                    self.logger.info(f"Started prompt update listener for {self.name}")
                else:
                    self.logger.warning(f"No running asyncio loop for {self.name}, prompt listener not started.")
            except RuntimeError:
                self.logger.warning(f"No running asyncio loop for {self.name} (RuntimeError), prompt listener not started.")
            except Exception as e:
                self.logger.error(f"Error starting prompt listener for {self.name}: {e}")
        else:
            self.logger.info(f"Prompt listener not started for {self.name} (no orchestrator_ref or not live)")

    async def _listen_for_prompt_updates(self):
        """Listens to Redis pub/sub for prompt_updated events and hot-swaps."""
        r_client = None
        pubsub = None
        redis_host = os.getenv("LEGION_REDIS_HOST", "localhost")
        redis_port = int(os.getenv("LEGION_REDIS_PORT", 7600))
        prompts_events_channel = "prompts:events"

        while True:
            try:
                self.logger.info(f"[{self.name}] Prompt listener: Connecting to Redis...")
                r_client = redis.asyncio.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=5)
                await r_client.ping()
                pubsub = r_client.pubsub()
                await pubsub.subscribe(prompts_events_channel)
                self.logger.info(f"[{self.name}] Prompt listener: Subscribed to {prompts_events_channel}")

                async for message in pubsub.listen():
                    if message and message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            if data.get("agent") == self.name and data.get("event") == "prompt_updated":
                                payload = data.get("payload", {})
                                new_system_prompt = payload.get("system")
                                new_skills = payload.get("skills")

                                if new_system_prompt is not None:
                                    self.system_prompt = html.unescape(new_system_prompt)
                                    self.logger.info(f"[{self.name}] Hot-reloaded system_prompt.")

                                if new_skills is not None:
                                    self.skills = new_skills
                                    self.logger.info(f"[{self.name}] Hot-reloaded skills: {self.skills}")

                        except json.JSONDecodeError as e:
                            self.logger.error(f"[{self.name}] Prompt listener: Error decoding JSON: {e} - Data: {message['data']}")
                        except Exception as e:
                            self.logger.error(f"[{self.name}] Prompt listener: Error processing message: {e}")
            except redis.exceptions.ConnectionError as e:
                self.logger.error(f"[{self.name}] Prompt listener: Redis connection error: {e}. Retrying in 10s...")
            except Exception as e:
                self.logger.error(f"[{self.name}] Prompt listener: Unexpected error: {e}. Retrying in 10s...")
            finally:
                if pubsub:
                    try:
                        await pubsub.unsubscribe(prompts_events_channel)
                        self.logger.info(f"[{self.name}] Prompt listener: Unsubscribed from {prompts_events_channel}")
                    except Exception as e_unsub:
                        self.logger.error(f"[{self.name}] Prompt listener: Error unsubscribing: {e_unsub}")
                if r_client:
                    try:
                        await r_client.close()
                        self.logger.info(f"[{self.name}] Prompt listener: Redis client closed.")
                    except Exception as e_close:
                        self.logger.error(f"[{self.name}] Prompt listener: Error closing Redis client: {e_close}")

            await asyncio.sleep(10)

    async def post_to_discord(self, message):
        """Post a message to the agent's Discord channel, splitting if too long."""
        try:
            # Import here to avoid circular imports
            from legion.utils.discord_bridge import MessageType, send_discord_embed

            # Determine message type based on content
            msg_type = MessageType.INFO
            if "[Error]" in message or "ERROR" in message.upper():
                msg_type = MessageType.ERROR
            elif "[Warning]" in message or "WARNING" in message.upper():
                msg_type = MessageType.WARNING
            elif "[Assessment]" in message or "SUCCESS" in message.upper():
                msg_type = MessageType.SUCCESS

            # Get agent-specific channel ID from environment
            agent_channel_var = f"{self.name.upper()}_CHANNEL_ID"
            channel_id = int(os.getenv(agent_channel_var, 0))

            # Fallback to orchestrator's channel mapping if no env var
            if not channel_id and hasattr(self, "orchestrator"):
                channel_id = self.orchestrator.agent_channel_ids.get(self.name, 0)

            # Final fallback to agent feed channel
            if not channel_id:
                channel_id = int(os.getenv("AGENT_FEED_CHANNEL_ID", 0))

            if channel_id:
                # Use the new discord bridge for better formatting
                success = await send_discord_embed(
                    self.name, message, msg_type, channel_id=channel_id
                )
                if not success:
                    logging.warning(
                        f"[BaseAgent] Failed to send Discord message for {self.name}"
                    )
            else:
                logging.error(f"[BaseAgent] No channel ID found for agent {self.name}")

        except Exception as e:
            logging.error(f"[BaseAgent] Error in post_to_discord for {self.name}: {e}")
            # Fallback to old method if new bridge fails
            await self._post_to_discord_fallback(message)

    async def _post_to_discord_fallback(self, message):
        """Fallback Discord posting method using the old approach."""
        channel_id = (
            self.orchestrator.agent_channel_ids.get(self.name)
            if hasattr(self, "orchestrator")
            else None
        )
        if not channel_id:
            logging.error(f"[BaseAgent] No channel_id found for agent {self.name}")
            return
        if self.client is None and hasattr(self.orchestrator, "client"):
            self.client = self.orchestrator.client
        channel = self.client.get_channel(channel_id) if self.client else None
        emoji = AGENT_EMOJIS.get(self.name, "")
        prefix = f"{emoji} **{self.name}** "
        # Discord max message length is 2000 chars
        MAX_LEN = 2000
        if not channel:
            logging.warning(
                f"[BaseAgent] Channel {channel_id} not found for agent {self.name}"
            )
            return
        # Split message if too long
        if len(message) > MAX_LEN:
            chunks = []
            lines = message.split("\n")
            chunk = ""
            for line in lines:
                if len(chunk) + len(line) + 1 > MAX_LEN:
                    chunks.append(chunk)
                    chunk = line
                else:
                    chunk += ("\n" if chunk else "") + line
            if chunk:
                chunks.append(chunk)
            for i, chunk in enumerate(chunks):
                suffix = f"\n[Message chunk {i + 1}/{len(chunks)}]"
                to_send = chunk + suffix if i == len(chunks) - 1 else chunk
                await channel.send(f"{prefix}{to_send}")
        else:
            await channel.send(f"{prefix}{message}")

    async def send_status_update(
        self, status: str, details: Optional[Dict[str, Any]] = None
    ):
        """Send a formatted status update to Discord."""
        try:
            from legion.utils.discord_bridge import MessageType, send_discord_embed

            fields = []
            if details:
                for key, value in details.items():
                    fields.append((key.title(), str(value)))

            await send_discord_embed(self.name, status, MessageType.INFO, fields=fields)
        except Exception as e:
            logging.error(f"[BaseAgent] Error sending status update: {e}")

    async def send_error_notification(self, error: str, context: Optional[str] = None):
        """Send a formatted error notification to Discord."""
        try:
            from legion.utils.discord_bridge import MessageType, send_discord_embed

            fields = []
            if context:
                fields.append(("Context", context))

            await send_discord_embed(
                self.name, f"Error: {error}", MessageType.ERROR, fields=fields
            )
        except Exception as e:
            logging.error(f"[BaseAgent] Error sending error notification: {e}")

    async def send_success_notification(
        self, message: str, metrics: Optional[Dict[str, Any]] = None
    ):
        """Send a formatted success notification to Discord."""
        try:
            from legion.utils.discord_bridge import MessageType, send_discord_embed

            fields = []
            if metrics:
                for key, value in metrics.items():
                    fields.append((key.title(), str(value)))

            await send_discord_embed(
                self.name, message, MessageType.SUCCESS, fields=fields
            )
        except Exception as e:
            logging.error(f"[BaseAgent] Error sending success notification: {e}")

    async def log_to_feed(self, skill_name: str, status: str, input_summary: Any, output_summary: Any, message_type=None):
        """Helper to send structured logs to the agent-feed channel."""
        try:
            from legion.utils.discord_bridge import MessageType, send_discord_embed

            # Default message type if not provided
            if message_type is None:
                message_type = MessageType.INFO

            timestamp = datetime.now(timezone.utc).isoformat()
            details = [
                ("Timestamp", timestamp),
                ("Skill Name", skill_name),
                ("Input Summary", str(input_summary)[:1000]),
                ("Output/Result", str(output_summary)[:1000]),
                ("Status", status)
            ]

            # Use agent feed channel ID from environment
            agent_feed_channel_id = int(os.getenv("AGENT_FEED_CHANNEL_ID", 1362902052279291904))

            await send_discord_embed(
                agent_name=self.name,
                message=f"{skill_name} Executed",
                msg_type=message_type,
                channel_id=agent_feed_channel_id,
                fields=details
            )
        except Exception as e:
            logging.error(f"[BaseAgent] Error in log_to_feed for {self.name}: {e}")

    async def self_assess(self):
        """Run a self-assessment and post the result to Discord."""
        logging.info(f"[BaseAgent] {self.name} running self_assess()")
        assessment = await self.handle_message(
            content="Please self-assess your current state and summarize your next actions.",
            author=self.name,
            timestamp=None,
        )
        await self.post_to_discord(f"[Assessment] {assessment}")

    async def handle_message(
        self, content=None, author=None, timestamp=None, context=None
    ):
        """Handle a message, manage memory, and interact with LLM and Discord."""
        try:
            # Emit introduction on first message
            if not self.introduced:
                try:
                    if hasattr(self, "system_prompt") and self.system_prompt:
                        first_line = self.system_prompt.strip().splitlines()[0]
                    else:
                        first_line = "Ready to assist."
                except Exception as e:
                    logging.warning(f"[{self.name}] Failed to build introduction: {e}")
                    first_line = "Ready to assist."
                intro = f"{AGENT_EMOJIS.get(self.name, '')} **{self.name}** here! {first_line}"
                await self.post_to_discord(intro)
                self.introduced = True
            user_query = (
                content
                if content is not None
                else (context["content"] if context else "")
            )
            timestamp = (
                timestamp
                if timestamp is not None
                else (
                    context["timestamp"] if context and "timestamp" in context else None
                )
            )
            thread_id = (
                timestamp.isoformat()
                if hasattr(timestamp, "isoformat")
                else str(timestamp)
            )
            # 1. Persona system prompt
            try:
                if hasattr(self, "system_prompt") and self.system_prompt:
                    system_prompt = self.system_prompt.strip()
                else:
                    system_prompt = (
                        self.config.get("default_prompt")
                        or "You are a helpful assistant."
                    )
            except AttributeError as e:
                logging.error(
                    f"[{self.name}] Failed to load system prompt due to attribute error: {e}"
                )
                system_prompt = "You are a helpful assistant."
            except KeyError as e:
                logging.error(
                    f"[{self.name}] Failed to load system prompt due to missing key: {e}"
                )
                system_prompt = "You are a helpful assistant."
            # 2. Retrieve long-term memory via helper
            try:
                message_embedding = self.get_message_embedding(user_query)
                top_k = self.config.get("memory_top_k", 3)
                memories = self.mem_retrieve(
                    message_embedding,
                    top_k,
                    tags=self.config.get("memory_tags"),
                    timestamp=timestamp,
                )
            except RuntimeError as e:
                logging.warning(
                    f"[{self.name}] Failed to retrieve memories due to runtime error: {e}"
                )
                memories = []
            except ValueError as e:
                logging.warning(
                    f"[{self.name}] Failed to retrieve memories due to value error: {e}"
                )
                memories = []
            # 3. Fetch conversation history (last 5 messages)
            try:
                channel_id = self.orchestrator.agent_channel_ids.get(self.name)
                thread_history = await self.fetch_thread_history(
                    channel_id, thread_id, 5
                )
            except RuntimeError as e:
                logging.error(
                    f"[{self.name}] Failed to fetch thread history due to runtime error: {e}"
                )
                thread_history = []
            except AttributeError as e:
                logging.error(
                    f"[{self.name}] Failed to fetch thread history due to attribute error: {e}"
                )
                thread_history = []
            # 4. Build LLM payload using PromptBuilder
            messages = PromptBuilder.build(
                system_prompt=system_prompt,
                memories=memories,
                thread_history=thread_history,
                user_query=user_query,
            )
            # 5. Call LLM with per-agent overrides (model, temperature)
            override_kwargs: Dict[str, Any] = {}
            if "model" in self.config:
                override_kwargs["model"] = self.config["model"]
            if "temperature" in self.config:
                override_kwargs["temperature"] = self.config["temperature"]
            try:
                start_time = time.time()
                reply = self.call_llm(thread_id, messages, **override_kwargs)
                end_time = time.time()
                # Record latency metric
                try:
                    if hasattr(self, "orchestrator") and hasattr(
                        self.orchestrator, "state"
                    ):
                        self.orchestrator.state.log_task(
                            {
                                "type": "llm_latency",
                                "agent": self.name,
                                "latency": end_time - start_time,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                except AttributeError as e:
                    logging.warning(
                        f"[{self.name}] Failed to log latency due to attribute error: {e}"
                    )
                except RuntimeError as e:
                    logging.warning(
                        f"[{self.name}] Failed to log latency due to runtime error: {e}"
                    )
                print(f"[DEBUG] LLM raw response: {reply}")
                # Check for 'choices' in the response
                if hasattr(reply, "choices") or (
                    isinstance(reply, dict) and "choices" in reply
                ):
                    print("[DEBUG] SUCCESS: 'choices' field found in response.")
                else:
                    print(
                        "[DEBUG] ERROR: 'choices' field NOT found in response! Check LM Studio model and config."
                    )
                # Return the assistant reply as before
                return reply
            except RuntimeError as e:
                logging.error(
                    f"[{self.name}] LLM call failed due to runtime error: {e}"
                )
                reply = "[Error: LLM unavailable]"
            except ValueError as e:
                logging.error(f"[{self.name}] LLM call failed due to value error: {e}")
                reply = "[Error: LLM unavailable]"
            # 6. Post reply to Discord
            try:
                await self.post_to_discord(reply)
            except RuntimeError as e:
                logging.error(
                    f"[{self.name}] Failed to post reply to Discord due to runtime error: {e}"
                )
            except AttributeError as e:
                logging.error(
                    f"[{self.name}] Failed to post reply to Discord due to attribute error: {e}"
                )
            # 7. Append to SQLite memory log
            try:
                # Ensure user_query is serializable
                serializable_query = user_query
                if isinstance(user_query, dict):
                    serializable_query = user_query.copy()
                    if "timestamp" in serializable_query and hasattr(
                        serializable_query["timestamp"], "isoformat"
                    ):
                        serializable_query["timestamp"] = serializable_query[
                            "timestamp"
                        ].isoformat()
                self.memory.log_task(
                    {"type": "user_message", "content": serializable_query}
                )
                self.memory.log_task({"type": "assistant_reply", "content": reply})
            except RuntimeError as e:
                logging.error(
                    f"[{self.name}] Failed to append to SQLite memory due to runtime error: {e}"
                )
            except ValueError as e:
                logging.error(
                    f"[{self.name}] Failed to append to SQLite memory due to value error: {e}"
                )
            # 8. Store vector memories with tags/timestamp
            try:
                # Generate embedding for reply
                reply_embedding = self.get_message_embedding(reply)
                self.mem_store(
                    [
                        {"text": user_query, "embedding": message_embedding},
                        {"text": reply, "embedding": reply_embedding},
                    ],
                    tags=self.config.get("memory_tags"),
                    timestamp=timestamp,
                )
            except RuntimeError as e:
                logging.error(
                    f"[{self.name}] Failed to store vector memories due to runtime error: {e}"
                )
            except ValueError as e:
                logging.error(
                    f"[{self.name}] Failed to store vector memories due to value error: {e}"
                )
            return reply
        except Exception as e:
            logging.error(
                f"[{self.name}] Unhandled exception in handle_message: {e}",
                exc_info=True,
            )
            # Fallback generic error handling
            with contextlib.suppress(Exception):
                await self.post_to_discord(f"[Error] Internal error in {self.name}.")
            return "[Error: Internal error in message processing]"

    def get_message_embedding(self, text: str) -> List[float]:
        """Generate an embedding for the given text, safely handling errors."""
        model = self.config.get("embedding_model", "text-embedding-ada-002")
        if not model:
            raise RuntimeError(
                f"[{self.name}] No embedding model loaded. Please load a model before requesting embeddings."
            )
        try:
            response = openai.Embedding.create(
                input=[text],
                model=model,
            )
            if (hasattr(response, "data") and response.data) or (
                isinstance(response, dict) and "data" in response and response["data"]
            ):
                return response["data"][0]["embedding"]
            else:
                print(
                    "[DEBUG] Embedding response missing 'data', returning zero-vector fallback."
                )
                return [0.0] * 1536  # fallback dimension
        except Exception as e:
            logging.warning(f"[{self.name}] Embedding creation failed: {e}")
            raise RuntimeError(f"[{self.name}] Embedding creation failed: {e}")

    async def fetch_thread_history(
        self, channel_id: int, thread_id: str, limit: int
    ) -> List[Dict[str, str]]:
        """Fetch the last N messages from a Discord channel thread."""
        logging.info(
            f"[BaseAgent] Fetching last {limit} messages from channel {channel_id}"
        )
        try:
            if not self.client:
                logging.warning("[BaseAgent] No client for fetch_thread_history")
                return []
            channel = self.client.get_channel(channel_id)
            if not channel:
                logging.warning(
                    f"[BaseAgent] Channel {channel_id} not found in fetch_thread_history"
                )
                return []
            history = []
            async for msg in channel.history(limit=limit):
                role = "assistant" if msg.author.bot else "user"
                history.append({"role": role, "content": msg.content})
            return list(reversed(history))
        except AttributeError as e:
            logging.error(f"[BaseAgent] Attribute error in fetch_thread_history: {e}")
            return []
        except RuntimeError as e:
            logging.error(f"[BaseAgent] Runtime error in fetch_thread_history: {e}")
            return []

    def call_llm(
        self, thread_id: str, history: List[Dict[str, str]], **override_kwargs
    ) -> str:
        """Centralized LLM invocation: selects dynamic rules and calls the LLM client."""
        if not self.llm.model:
            raise RuntimeError(
                f"[{self.name}] No LLM model loaded. Please load a model before requesting completions."
            )
        print(
            f"[DEBUG] {self.name} calling LLM with model={self.llm.model} base={openai.api_base}"
        )
        print(
            f"[DEBUG] LLM request params: thread_id={thread_id}, history={history}, overrides={override_kwargs}"
        )
        try:
            start_time = time.time()
            # Build the params as the OpenAI SDK would
            params = {**self.llm.default_kwargs, **override_kwargs}
            params["model"] = self.llm.model
            params["messages"] = history
            print(f"[DEBUG] LLM raw params: {params}")
            # Actually call the LLM
            response = openai.ChatCompletion.create(**params)
            end_time = time.time()
            # Record latency metric
            try:
                if hasattr(self, "orchestrator") and hasattr(
                    self.orchestrator, "state"
                ):
                    self.orchestrator.state.log_task(
                        {
                            "type": "llm_latency",
                            "agent": self.name,
                            "latency": end_time - start_time,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )
            except AttributeError as e:
                logging.warning(
                    f"[{self.name}] Failed to log latency metric due to attribute error: {e}"
                )
            except RuntimeError as e:
                logging.warning(
                    f"[{self.name}] Failed to log latency metric due to runtime error: {e}"
                )
            print(f"[DEBUG] LLM raw response: {response}")
            # Check for 'choices' in the response
            if hasattr(response, "choices") or (
                isinstance(response, dict) and "choices" in response
            ):
                print("[DEBUG] SUCCESS: 'choices' field found in response.")
            else:
                print(
                    "[DEBUG] ERROR: 'choices' field NOT found in response! Check LM Studio model and config."
                )
            # Return the assistant reply as before
            return response.choices[0].message.content
        except openai.error.OpenAIError as e:
            import traceback

            print(f"[ERROR] LLM call failed: {e}")
            traceback.print_exc()
            raise RuntimeError(
                f"[{self.name}] LLM call failed due to OpenAI error: {e}"
            )
        except ValueError as e:
            import traceback

            print(f"[ERROR] LLM call failed: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[{self.name}] LLM call failed due to value error: {e}")

    def start_self_assessment(self, interval_seconds=600):
        """Start the self-assessment loop if not already running."""
        with self._self_assessment_lock:
            if self._self_assessment_running:
                logging.info(
                    f"[BaseAgent] Self-assessment loop already running for {self.name}. Ignoring duplicate start."
                )
                return False
            self._self_assessment_running = True

        def loop():
            import asyncio

            try:
                while self._self_assessment_running:
                    coro = self.self_assess()
                    try:
                        asyncio.run(coro)
                    except RuntimeError:
                        # If already in event loop, schedule as task
                        asyncio.get_event_loop().create_task(coro)
                    for _ in range(interval_seconds):
                        if not self._self_assessment_running:
                            break
                        time.sleep(1)
            finally:
                self._self_assessment_running = False

        t = threading.Thread(target=loop, daemon=True)
        t.start()
        logging.info(f"[BaseAgent] Started self-assessment loop for {self.name}.")
        return True

    def stop_self_assessment(self):
        with self._self_assessment_lock:
            self._self_assessment_running = False
        logging.info(f"[BaseAgent] Stopped self-assessment loop for {self.name}.")

    def mem_retrieve(
        self,
        embedding: List[float],
        top_k: int,
        tags: Optional[List[str]] = None,
        timestamp: Optional[Any] = None,
        base_dir: Optional[str] = None,
    ) -> List[str]:
        """Helper to retrieve vector memories with optional tags and timestamp."""
        bd = base_dir or self.config.get("memory_base_dir", "memory")
        return LegionAgentMemory.retrieve_memories(
            self.name, embedding, top_k, base_dir=bd
        )

    def mem_store(
        self,
        snippets: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
        timestamp: Optional[Any] = None,
        base_dir: Optional[str] = None,
    ) -> None:
        """Helper to store vector memories with optional tags, timestamp; deduplicates by text."""
        bd = base_dir or self.config.get("memory_base_dir", "memory")

        # Deduplicate by text
        def make_hashable_text(text):
            if isinstance(text, dict):
                import json

                return json.dumps(text, sort_keys=True)
            return str(text)

        unique = {
            make_hashable_text(snip["text"]): snip
            for snip in snippets
            if isinstance(snip, dict) and "text" in snip and "embedding" in snip
        }
        enriched = []
        for snip in unique.values():
            item = {"text": snip["text"], "embedding": snip["embedding"]}
            if tags:
                item["tags"] = tags
            if timestamp:
                item["timestamp"] = (
                    timestamp.isoformat()
                    if hasattr(timestamp, "isoformat")
                    else str(timestamp)
                )
            enriched.append(item)
        LegionAgentMemory.store_memories(self.name, enriched, base_dir=bd)

    async def store_message(
        self, payload: str, message_id: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Store a message in the agent's memory."""
        message: Dict[str, Any] = {
            "id": message_id,
            "role": "user",
            "content": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {"source": "direct_message", "agent": self.name},
        }
        # Store user message (will be deduplicated)
        await self.memory.store_memory(
            message_id, payload, metadata=message["metadata"]
        )
