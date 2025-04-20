import logging
from typing import Any, Dict, List
from core.utils.llm_client import LLMClient
import openai
logging.getLogger("openai").setLevel(logging.WARNING)
from memory.legion_memory import LegionAgentMemory
from datetime import datetime
import threading
import time

AGENT_EMOJIS = {
    "architect_agent": "🏗️",
    "metrics_agent":   "📊",
    "ux_designer_agent":"🎨",
    "therapist_agent": "🗣️",
    "ping_agent":      "📶",
    "echo_agent":      "🔁",
    "healthcheck_agent":"✅",
}

class BaseAgent:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.name = self.__class__.__name__.replace('Agent', '').lower() + '_agent'
        self.client = None
        self.channel_id = getattr(orchestrator, 'agent_channel_ids', {}).get(self.name, 0)
        self.config = {}
        self.llm = LLMClient()
        self.dynamic_rules = {}
        self.memory = LegionAgentMemory(self.name)
        # Track if agent has introduced itself
        self.introduced = False
        self._self_assessment_running = False
        self._self_assessment_lock = threading.Lock()

    async def post_to_discord(self, message):
        # Always resolve channel from orchestrator mapping
        channel_id = self.orchestrator.agent_channel_ids.get(self.name)
        if not channel_id:
            logging.error(f"[BaseAgent] No channel_id found for agent {self.name}")
            return
        if self.client is None and hasattr(self.orchestrator, 'client'):
            self.client = self.orchestrator.client
        channel = self.client.get_channel(channel_id) if self.client else None
        emoji = AGENT_EMOJIS.get(self.name, "")
        prefix = f"{emoji} **{self.name}** "
        # Discord max message length is 2000 chars
        MAX_LEN = 2000
        if not channel:
            logging.warning(f"[BaseAgent] Channel {channel_id} not found for agent {self.name}")
            return
        # Split message if too long
        if len(message) > MAX_LEN:
            chunks = []
            lines = message.split('\n')
            chunk = ""
            for line in lines:
                if len(chunk) + len(line) + 1 > MAX_LEN:
                    chunks.append(chunk)
                    chunk = line
                else:
                    chunk += ('\n' if chunk else '') + line
            if chunk:
                chunks.append(chunk)
            for i, chunk in enumerate(chunks):
                suffix = f"\n[Message chunk {i+1}/{len(chunks)}]"
                to_send = (chunk + suffix) if i == len(chunks)-1 else chunk
                await channel.send(f"{prefix}{to_send}")
        else:
            await channel.send(f"{prefix}{message}")

    async def self_assess(self):
        logging.info(f"[BaseAgent] {self.name} running self_assess()")
        assessment = await self.handle_message(
            content="Please self-assess your current state and summarize your next actions.",
            author=self.name,
            timestamp=None
        )
        await self.post_to_discord(f"[Assessment] {assessment}")

    async def handle_message(self, content=None, author=None, timestamp=None, context=None):
        """
        Unified message handling for all agents with memory and thread-awareness.
        """
        # Emit introduction on first message
        if not self.introduced:
            first_line = self.system_prompt.strip().splitlines()[0]
            intro = f"{AGENT_EMOJIS.get(self.name,'')} **{self.name}** here! {first_line}"
            await self.post_to_discord(intro)
            self.introduced = True
        user_query = content if content is not None else (context["content"] if context else "")
        timestamp = timestamp if timestamp is not None else (context["timestamp"] if context and "timestamp" in context else None)
        thread_id = (
            timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp)
        )
        # 1. Persona system prompt
        try:
            if hasattr(self, "system_prompt") and self.system_prompt:
                system_prompt = self.system_prompt.strip()
            else:
                system_prompt = self.config.get("default_prompt") or "You are a helpful assistant."
        except Exception as e:
            logging.error(f"[{self.name}] Failed to load system prompt: {e}")
            system_prompt = "You are a helpful assistant."
        # 2. Retrieve long-term memory
        try:
            message_embedding = self.get_message_embedding(user_query)
            memories = self.memory.retrieve_memories(self.name, message_embedding, 3)
        except Exception as e:
            logging.warning(f"[{self.name}] Failed to retrieve memories: {e}")
            memories = []
        if memories:
            memories_msg = "Previously on our project: " + "\n".join(memories)
        else:
            memories_msg = "Previously on our project: (no relevant memories found)"
        # 3. Fetch conversation history (last 5 messages)
        try:
            channel_id = self.orchestrator.agent_channel_ids.get(self.name)
            thread_history = await self.fetch_thread_history(channel_id, thread_id, 5)
        except Exception as e:
            logging.error(f"[{self.name}] Failed to fetch thread history: {e}")
            thread_history = []
        # 4. Build LLM payload
        messages = []
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "system", "content": memories_msg})
        messages.append({"role": "system", "content": "Reflection: think step-by-step before answering."})
        messages.extend(thread_history)
        messages.append({"role": "user", "content": user_query})
        # 5. Call LLM
        try:
            reply = self.call_llm(thread_id, messages)
        except Exception as e:
            logging.error(f"[{self.name}] LLM call failed: {e}")
            reply = "[Error: LLM unavailable]"
        # 6. Post reply to Discord
        try:
            await self.post_to_discord(reply)
        except Exception as e:
            logging.error(f"[{self.name}] Failed to post reply to Discord: {e}")
        # 7. Append to memory using the proper memory API
        try:
            self.memory.log_task({"type": "user_message", "content": user_query})
            self.memory.log_task({"type": "assistant_reply", "content": reply})
        except Exception as e:
            logging.error(f"[{self.name}] Failed to append to memory: {e}")
        return reply

    def get_message_embedding(self, text: str) -> List[float]:
        # Generate an embedding for the given text, safely handling errors
        model = self.config.get("embedding_model", "text-embedding-ada-002")
        if not model:
            raise RuntimeError(f"[{self.name}] No embedding model loaded. Please load a model before requesting embeddings.")
        try:
            response = openai.Embedding.create(
                input=[text],
                model=model,
            )
            if hasattr(response, 'data') and response.data:
                return response["data"][0]["embedding"]
            elif isinstance(response, dict) and "data" in response and response["data"]:
                return response["data"][0]["embedding"]
            else:
                print("[DEBUG] Embedding response missing 'data', returning zero-vector fallback.")
                return [0.0] * 1536  # fallback dimension
        except Exception as e:
            logging.warning(f"[{self.name}] Embedding creation failed: {e}")
            raise RuntimeError(f"[{self.name}] Embedding creation failed: {e}")

    async def fetch_thread_history(
        self, channel_id: int, thread_id: str, limit: int
    ) -> List[Dict[str, str]]:
        logging.info(f"[BaseAgent] Fetching last {limit} messages from channel {channel_id}")
        try:
            if not self.client:
                logging.warning(f"[BaseAgent] No client for fetch_thread_history")
                return []
            channel = self.client.get_channel(channel_id)
            if not channel:
                logging.warning(f"[BaseAgent] Channel {channel_id} not found in fetch_thread_history")
                return []
            history = []
            async for msg in channel.history(limit=limit):
                role = "assistant" if msg.author.bot else "user"
                history.append({"role": role, "content": msg.content})
            return list(reversed(history))
        except Exception as e:
            logging.error(f"[BaseAgent] Exception in fetch_thread_history: {e}")
            return []

    def call_llm(
        self, thread_id: str, history: List[Dict[str, str]], **override_kwargs
    ) -> str:
        """
        Centralized LLM invocation: selects dynamic rules and calls the LLM client.
        """
        if not self.llm.model:
            raise RuntimeError(f"[{self.name}] No LLM model loaded. Please load a model before requesting completions.")
        print(f"[DEBUG] {self.name} calling LLM with model={self.llm.model} base={openai.api_base}")
        print(f"[DEBUG] LLM request params: thread_id={thread_id}, history={history}, overrides={override_kwargs}")
        try:
            # Build the params as the OpenAI SDK would
            params = {**self.llm.default_kwargs, **override_kwargs}
            params["model"] = self.llm.model
            params["messages"] = history
            print(f"[DEBUG] LLM raw params: {params}")
            # Actually call the LLM
            response = openai.ChatCompletion.create(**params)
            print(f"[DEBUG] LLM raw response: {response}")
            # Check for 'choices' in the response
            if hasattr(response, 'choices') or (isinstance(response, dict) and 'choices' in response):
                print("[DEBUG] SUCCESS: 'choices' field found in response.")
            else:
                print("[DEBUG] ERROR: 'choices' field NOT found in response! Check LM Studio model and config.")
            # Return the assistant reply as before
            return response.choices[0].message.content
        except Exception as e:
            import traceback
            print(f"[ERROR] LLM call failed: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[{self.name}] LLM call failed: {e}")

    def start_self_assessment(self, interval_seconds=600):
        """Start the self-assessment loop if not already running."""
        with self._self_assessment_lock:
            if self._self_assessment_running:
                logging.info(f"[BaseAgent] Self-assessment loop already running for {self.name}. Ignoring duplicate start.")
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
