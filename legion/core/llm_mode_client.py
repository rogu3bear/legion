"""Mode-switching LLM Client for Legion."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from legion.core.interfaces import ILLMClient

logger = logging.getLogger(__name__)


class ModeSwitchingLLMClient(ILLMClient):
    """LLM Client that switches between local and remote modes based on configuration."""

    def __init__(
        self,
        mode: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        **default_kwargs: Any,
    ):
        """
        Initialize the mode-switching LLM client.

        Args:
            mode: 'local' for LM Studio, 'remote' for OpenAI, or None for env-based detection
            api_key: API key for remote services
            model: Model identifier
            api_base: Base URL override
            **default_kwargs: Default parameters for requests
        """
        self.mode = mode or os.getenv("LLM_MODE", "remote")
        self.model = model or os.getenv("OPENAI_MODEL", "meta-llama-3.1-8b-instruct")
        self.default_kwargs = default_kwargs or {}

        logger.info(f"ModeSwitchingLLMClient initialized in {self.mode} mode")

        # Initialize backends based on mode
        if self.mode.lower() == "local":
            try:
                from legion.mcp.bridges.lmstudio_bridge import LMStudioAdapter
                self.lmstudio_adapter = LMStudioAdapter(api_base)
                logger.info("Local LM Studio adapter initialized")
            except ImportError as e:
                logger.error(f"Failed to import LM Studio adapter: {e}")
                logger.warning("Falling back to remote mode")
                self.mode = "remote"
                self._init_remote_client(api_key, api_base)
        else:
            self._init_remote_client(api_key, api_base)

    def _init_remote_client(self, api_key: Optional[str], api_base: Optional[str]):
        """Initialize remote OpenAI client."""
        try:
            import openai
            if api_base:
                openai.api_base = api_base
            elif os.getenv("OPENAI_API_BASE"):
                openai.api_base = os.getenv("OPENAI_API_BASE")

            openai.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
            self.openai = openai
            logger.info("Remote OpenAI client initialized")
        except ImportError as e:
            logger.error(f"Failed to import OpenAI client: {e}")
            raise RuntimeError("Neither local nor remote LLM client could be initialized")

    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call the LLM with a list of messages and return the response."""
        if self.mode.lower() == "local":
            return asyncio.run(self._call_local(messages, **kwargs))
        else:
            return self._call_remote_sync(messages, **kwargs)

    async def call_async(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Async version of call method."""
        if self.mode.lower() == "local":
            return await self._call_local(messages, **kwargs)
        else:
            return self._call_remote_sync(messages, **kwargs)

    async def _call_local(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call local LM Studio."""
        try:
            params = {**self.default_kwargs, **kwargs}
            response = await self.lmstudio_adapter.chat_complete(messages, **params)

            # Extract response text from various response formats
            if "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"]
            elif "generations" in response and response["generations"]:
                return response["generations"][0]["text"]
            else:
                logger.error(f"Unexpected local LLM response format: {response}")
                raise RuntimeError(f"Unexpected local LLM response format: {response}")

        except Exception as e:
            logger.error(f"Local LLM call failed: {e}")
            raise

    def _call_remote_sync(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call remote OpenAI API (synchronous)."""
        try:
            params = {**self.default_kwargs, **kwargs}
            params["model"] = params.get("model", self.model)
            params["messages"] = messages
            params["max_tokens"] = params.get("max_tokens", 1024)

            response = self.openai.ChatCompletion.create(**params)

            # Extract response text
            if hasattr(response, "choices"):
                return response.choices[0].message.content
            elif isinstance(response, dict) and "choices" in response:
                return response["choices"][0]["message"]["content"]
            else:
                logger.error(f"Unexpected remote LLM response format: {response}")
                raise RuntimeError(f"Unexpected remote LLM response format: {response}")

        except Exception as e:
            logger.error(f"Remote LLM call failed: {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """Generate an embedding for the given text."""
        if self.mode.lower() == "local":
            # For local mode, we might need to implement embedding endpoint
            # For now, return a placeholder or use a different service
            logger.warning("Embedding not implemented for local mode, returning placeholder")
            return [0.0] * 384  # Common embedding dimension
        else:
            # Use OpenAI embeddings
            try:
                response = self.openai.Embedding.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                return response["data"][0]["embedding"]
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                raise

    def generate(
        self,
        agent_name: str,
        thread_id: str,
        dynamic_rules: Dict[str, Any],
        history: List[Dict[str, str]],
        **override_kwargs: Any,
    ) -> str:
        """
        Legacy generate method for backward compatibility with existing code.
        """
        # Select rules for this thread
        rules = dynamic_rules.get(thread_id, dynamic_rules.get("default", []))

        # Build the messages sequence
        messages: List[Dict[str, str]] = []
        if isinstance(rules, list):
            messages.extend(rules)
        elif isinstance(rules, dict):
            messages.append(rules)

        # Append conversation history
        messages.extend(history)

        # Call the main method
        return self.call(messages, **override_kwargs)

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the LLM service."""
        if self.mode.lower() == "local":
            try:
                return await self.lmstudio_adapter.stats()
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "mode": "local",
                    "error": str(e)
                }
        else:
            # For remote, try a simple API call
            try:
                test_response = self.call([{"role": "user", "content": "test"}], max_tokens=1)
                return {
                    "status": "healthy",
                    "mode": "remote",
                    "test_response_length": len(test_response)
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "mode": "remote",
                    "error": str(e)
                }


# Factory function for DI container
def create_mode_switching_llm_client() -> ModeSwitchingLLMClient:
    """Factory function to create mode-switching LLM client."""
    return ModeSwitchingLLMClient()
