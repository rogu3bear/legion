"""
LLMClient: Unified LLM interface wrapping OpenAI API.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import openai

# pick up our local LM Studio endpoint
base = os.getenv("OPENAI_API_BASE")
if base:
    # Ensure base URL includes /v1 prefix
    base = base.rstrip("/")
    if not base.endswith("/v1"):
        base = base + "/v1"
    openai.api_base = base
    print(f"DEBUG: openai.api_base = {openai.api_base}")
else:
    print("WARNING: OPENAI_API_BASE not set! LLM calls will fail.")
openai.api_key = os.getenv("OPENAI_API_KEY", "")
# API key is loaded silently to avoid leaking credentials
# print(f"DEBUG: openai.api_key  = {openai.api_key}")

# Configure logging
logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self
        api_key: Optional[str] = None
        model: Optional[str] = None
        api_base: Optional[str] = None
        **default_kwargs: Any
    ):
        """
        Initialize the LLM client with optional API key, model, base URL, and default parameters.
        """
        logger.info(
            "Initializing LLMClient", extra={"model": model, "api_base": api_base}
        )
        # Model identifier
        self.model = model or os.getenv("OPENAI_MODEL")
        # Default parameters for all requests (e.g., temperature, max_tokens)
        self.default_kwargs = default_kwargs or {}

    def generate(
        self
        agent_name: str
        thread_id: str
        dynamic_rules: Dict[str, Any]
        history: List[Dict[str, str]]
        **override_kwargs: Any
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
        params["model"] = self.model or "meta-llama-3.1-8b-instruct"
        params["messages"] = messages
        params["max_tokens"] = params.get("max_tokens", 1024)
        # Use the explicit /v1/chat/completions endpoint
        print(f"DEBUG: Calling /v1/chat/completions with model={params['model']}")
        response = openai.ChatCompletion.create(
            model=params["model"]
            messages=params["messages"]
            max_tokens=params["max_tokens"]
            **{
                k: v
                for k, v in params.items()
                if k not in ("model", "messages", "max_tokens")
            }
        )
        # Extract and return the assistant reply
        try:
            if hasattr(response, "choices"):
                return response.choices[0].message.content
            elif isinstance(response, dict) and "choices" in response:
                return response["choices"][0]["message"]["content"]
            elif isinstance(response, dict) and "generations" in response:
                return response["generations"][0]["text"]
            else:
                print(f"[ERROR] Unrecognized LLM response: {response}")
                raise RuntimeError(f"Unrecognized LLM response: {response}")
        except AttributeError as e:
            print(
                f"[ERROR] Exception parsing LLM response: {e}\nRaw response: {response}"
            )
            raise RuntimeError(f"Attribute error parsing LLM response: {e}")
        except KeyError as e:
            print(
                f"[ERROR] Exception parsing LLM response: {e}\nRaw response: {response}"
            )
            raise RuntimeError(f"Key error parsing LLM response: {e}")
