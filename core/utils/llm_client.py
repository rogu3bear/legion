"""
LLMClient: Unified LLM interface wrapping OpenAI API.
"""

import os
import openai
from typing import Any, Dict, List, Optional


class LLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        **default_kwargs: Any,
    ):
        """
        Initialize the LLM client with optional API key, model, base URL, and default parameters.
        """
        # Set API credentials and endpoint
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        if api_base:
            openai.api_base = api_base
            openai.api_type = "openai"
        # Model identifier
        self.model = model or os.getenv("OPENAI_MODEL")
        # Default parameters for all requests (e.g., temperature, max_tokens)
        self.default_kwargs = default_kwargs or {}

    def generate(
        self,
        agent_name: str,
        thread_id: str,
        dynamic_rules: Dict[str, Any],
        history: List[Dict[str, str]],
        **override_kwargs: Any,
    ) -> str:
        """
        Generate a completion using dynamic rules and history.

        Args:
            agent_name: Name of the agent making the call (for logging/tracing).
            thread_id: Identifier of the conversation thread (keys into dynamic_rules).
            dynamic_rules: Mapping of thread IDs to rule lists or messages.
            history: List of message dicts ({"role": ..., "content": ...}).
            override_kwargs: Any request params overriding defaults (e.g., temperature).

        Returns:
            The assistant's response string.
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

        # Merge parameters: defaults, overrides
        params: Dict[str, Any] = {**self.default_kwargs, **override_kwargs}
        # Ensure model and messages are provided
        params["model"] = self.model
        params["messages"] = messages

        # Perform the API call
        response = openai.ChatCompletion.create(**params)
        # Extract and return the assistant reply
        return response.choices[0].message.content
