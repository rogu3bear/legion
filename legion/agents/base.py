import logging
from typing import Any, Dict, List
from core.utils.llm_client import LLMClient
import openai


class BaseAgent:
    def __init__(
        self, name: str, client: Any, channel_id: int, config: Dict[str, Any] = None
    ):
        self.name = name
        self.client = client
        self.channel_id = channel_id
        # Agent configuration including LLM settings
        self.config = config or {}
        # Instantiate LLM client with dynamic API key/model and default parameters
        self.llm = LLMClient(
            api_key=self.config.get("llm_api_key"),
            model=self.config.get("llm_model"),
            api_base=self.config.get("llm_api_base"),
            **self.config.get("default_kwargs", {}),
        )
        # Dynamic rules for conversation threads
        self.dynamic_rules = self.config.get("dynamic_rules", {})

    async def post_to_discord(self, message):
        logging.info(
            f"[BaseAgent] {self.name} posting to channel {self.channel_id}: {message}"
        )
        channel = self.client.get_channel(self.channel_id)
        if channel:
            await channel.send(f"[{self.name}]: {message}")
        else:
            logging.warning(
                f"[BaseAgent] Channel {self.channel_id} not found for agent {self.name}"
            )

    async def self_assess(self):
        logging.info(f"[BaseAgent] {self.name} running self_assess()")
        prompt = "Please self-assess your current state and summarize your next actions."
        assessment = await self.handle_message({
            "content": prompt,
            "author": self.name,
            "timestamp": None
        })
        await self.post_to_discord(f"[Assessment] {assessment}")

    async def handle_message(self, context):
        """
        Unified message handling for all agents. Returns the LLM response string.
        Steps:
        1. Load default prompt from config (safe fallback)
        2. Retrieve top-K memories (safe fallback)
        3. Fetch thread history (safe fallback)
        4. Build LLM payload: system prompt, memory summary, thread, user
        5. Call LLM and return response
        All steps are error-wrapped and log failures.
        """
        content = context["content"]
        # author = context["author"]  # unused
        timestamp = context["timestamp"]
        thread_id = (
            timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp)
        )
        # 1. Default prompt
        try:
            default_prompt = (
                self.config.get("default_prompt") or "You are a helpful assistant."
            )
        except Exception as e:
            logging.error(f"[{self.name}] Failed to load default prompt: {e}")
            default_prompt = "You are a helpful assistant."
        # 2. Retrieve memories
        try:
            message_embedding = self.get_message_embedding(content)
            top_k = self.config.get("memory_top_k", 5)
            memories = self.retrieve_memories(self.name, message_embedding, top_k)
        except Exception as e:
            logging.error(f"[{self.name}] Failed to retrieve memories: {e}")
            memories = []
        # 3. Fetch thread history
        try:
            history_limit = self.config.get("history_limit", 10)
            thread_history = await self.fetch_thread_history(
                self.channel_id, thread_id, history_limit
            )
        except Exception as e:
            logging.error(f"[{self.name}] Failed to fetch thread history: {e}")
            thread_history = []
        # 4. Build LLM payload
        messages = []
        messages.append({"role": "system", "content": default_prompt})
        if memories:
            try:
                summary = self.summarize_memories(memories)
            except Exception as e:
                logging.error(f"[{self.name}] Failed to summarize memories: {e}")
                summary = "No relevant memories found."
            messages.append({"role": "system", "content": summary})
        else:
            messages.append(
                {"role": "system", "content": "No relevant memories found."}
            )
        messages.extend(thread_history)
        messages.append({"role": "user", "content": content})
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
        # 7. Extract and store new memory items
        try:
            new_memories = self.extract_memories(reply)
            self.store_memories(self.name, new_memories)
        except Exception as e:
            logging.error(f"[{self.name}] Failed to extract/store new memories: {e}")
        return reply

    def get_message_embedding(self, text: str) -> List[float]:
        # Generate an embedding for the given text
        response = openai.Embedding.create(
            input=[text],
            model=self.config.get("embedding_model", "text-embedding-ada-002"),
        )
        return response["data"][0]["embedding"]

    async def fetch_thread_history(
        self, channel_id: int, thread_id: str, limit: int
    ) -> List[Dict[str, str]]:
        logging.info(
            f"[BaseAgent] Fetching last {limit} messages from channel {channel_id}"
        )
        channel = self.client.get_channel(channel_id)
        if not channel:
            return []
        history = []
        async for msg in channel.history(limit=limit):
            role = "assistant" if msg.author.bot else "user"
            history.append({"role": role, "content": msg.content})
        return list(reversed(history))

    @staticmethod
    def retrieve_memories(
        agent_name: str, message_embedding: List[float], top_k: int
    ) -> List[str]:
        # Placeholder: integrate with vector-store memory index
        return []

    @staticmethod
    def summarize_memories(memories: List[str]) -> str:
        summary_lines = ["Relevant memories:"]
        summary_lines += [f"- {m}" for m in memories]
        return "\n".join(summary_lines)

    @staticmethod
    def extract_memories(text: str) -> List[str]:
        # Placeholder: extract new memory items via parsing or follow-up LLM call
        return []

    @staticmethod
    def store_memories(agent_name: str, memories: List[str]):
        # Placeholder: upsert memory items into the vector-store
        logging.info(f"[BaseAgent] Storing memories for {agent_name}: {memories}")

    def call_llm(
        self, thread_id: str, history: List[Dict[str, str]], **override_kwargs
    ) -> str:
        """
        Centralized LLM invocation: selects dynamic rules and calls the LLM client.
        """
        return self.llm.generate(
            self.name, thread_id, self.dynamic_rules, history, **override_kwargs
        )
