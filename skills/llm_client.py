"""
LLM Client for Legion MCP Server

This module provides a unified interface for interacting with different LLM providers
including LM Studio, OpenAI, and mock providers for testing.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import yaml

try:
    import openai
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None
    AsyncOpenAI = None

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client that can work with multiple providers."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the LLM client with configuration."""
        self.config = self._load_config(config_path)
        self.provider = self.config.get("provider", "mock")
        self.client = None
        self.async_client = None
        self._initialize_client()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file or environment variables."""
        if config_path is None:
            # Try to find the config file relative to this module
            config_path = Path(__file__).parent / "mcp_config.yaml"
        
        default_config = {
            "provider": "mock",
            "lm_studio": {
                "base_url": "http://localhost:1234/v1",
                "api_key": "not-needed",
                "model": "local-model",
                "max_tokens": 1000,
                "temperature": 0.3,
                "timeout_seconds": 30
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.3,
                "timeout_seconds": 30
            },
            "mock": {
                "enable_deterministic_responses": True,
                "response_delay_ms": 100
            }
        }
        
        try:
            if isinstance(config_path, (str, Path)) and Path(config_path).exists():
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config and "llm" in file_config:
                        llm_config = file_config["llm"]
                        # Expand environment variables in config
                        llm_config = self._expand_env_vars(llm_config)
                        default_config.update(llm_config)
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")
        
        # Override with environment variables
        if "LM_STUDIO_URL" in os.environ:
            default_config["lm_studio"]["base_url"] = os.environ["LM_STUDIO_URL"]
        if "LM_STUDIO_API_KEY" in os.environ:
            default_config["lm_studio"]["api_key"] = os.environ["LM_STUDIO_API_KEY"]
        if "OPENAI_API_KEY" in os.environ:
            default_config["openai"]["api_key"] = os.environ["OPENAI_API_KEY"]
        
        return default_config
    
    def _expand_env_vars(self, config: Any) -> Any:
        """Recursively expand environment variables in config values."""
        if isinstance(config, dict):
            return {key: self._expand_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._expand_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Handle ${VAR:-default} syntax
            if config.startswith("${") and config.endswith("}"):
                var_spec = config[2:-1]
                if ":-" in var_spec:
                    var_name, default_value = var_spec.split(":-", 1)
                    return os.getenv(var_name, default_value)
                else:
                    return os.getenv(var_spec, config)
            return config
        else:
            return config
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider configuration."""
        if not OPENAI_AVAILABLE and self.provider in ["openai", "lm_studio"]:
            logger.warning("OpenAI library not available, falling back to mock provider")
            self.provider = "mock"
        
        if self.provider == "lm_studio":
            self._initialize_lm_studio_client()
        elif self.provider == "openai":
            self._initialize_openai_client()
        elif self.provider == "mock":
            self._initialize_mock_client()
        else:
            logger.error(f"Unknown provider: {self.provider}, falling back to mock")
            self.provider = "mock"
            self._initialize_mock_client()
    
    def _initialize_lm_studio_client(self):
        """Initialize LM Studio client."""
        lm_config = self.config["lm_studio"]
        try:
            self.client = OpenAI(
                base_url=lm_config["base_url"],
                api_key=lm_config.get("api_key", "not-needed"),
                timeout=lm_config.get("timeout_seconds", 30)
            )
            self.async_client = AsyncOpenAI(
                base_url=lm_config["base_url"],
                api_key=lm_config.get("api_key", "not-needed"),
                timeout=lm_config.get("timeout_seconds", 30)
            )
            logger.info(f"Initialized LM Studio client with base_url: {lm_config['base_url']}")
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio client: {e}")
            self.provider = "mock"
            self._initialize_mock_client()
    
    def _initialize_openai_client(self):
        """Initialize OpenAI client."""
        openai_config = self.config["openai"]
        api_key = openai_config.get("api_key")
        
        if not api_key:
            logger.error("OpenAI API key not provided, falling back to mock")
            self.provider = "mock"
            self._initialize_mock_client()
            return
        
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=openai_config.get("base_url"),
                timeout=openai_config.get("timeout_seconds", 30)
            )
            self.async_client = AsyncOpenAI(
                api_key=api_key,
                base_url=openai_config.get("base_url"),
                timeout=openai_config.get("timeout_seconds", 30)
            )
            logger.info("Initialized OpenAI client")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.provider = "mock"
            self._initialize_mock_client()
    
    def _initialize_mock_client(self):
        """Initialize mock client for testing."""
        self.client = None
        self.async_client = None
        logger.info("Initialized mock LLM client")
    
    def _get_provider_config(self) -> Dict[str, Any]:
        """Get configuration for the current provider."""
        return self.config.get(self.provider, {})
    
    def complete_text(self, prompt: str, **kwargs) -> str:
        """Complete text using the configured LLM provider."""
        if self.provider == "mock":
            return self._mock_complete_text(prompt, **kwargs)
        
        try:
            provider_config = self._get_provider_config()
            
            # Merge provider config with kwargs
            params = {
                "model": provider_config.get("model", "gpt-3.5-turbo"),
                "max_tokens": provider_config.get("max_tokens", 1000),
                "temperature": provider_config.get("temperature", 0.3),
                **kwargs
            }
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                messages=messages,
                **params
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error completing text with {self.provider}: {e}")
            return f"[Error: Failed to complete text - {str(e)}]"
    
    async def complete_text_async(self, prompt: str, **kwargs) -> str:
        """Asynchronously complete text using the configured LLM provider."""
        if self.provider == "mock":
            return await self._mock_complete_text_async(prompt, **kwargs)
        
        try:
            provider_config = self._get_provider_config()
            
            # Merge provider config with kwargs
            params = {
                "model": provider_config.get("model", "gpt-3.5-turbo"),
                "max_tokens": provider_config.get("max_tokens", 1000),
                "temperature": provider_config.get("temperature", 0.3),
                **kwargs
            }
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.async_client.chat.completions.create(
                messages=messages,
                **params
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error completing text with {self.provider}: {e}")
            return f"[Error: Failed to complete text - {str(e)}]"
    
    def summarize_text(self, text: str, max_length: Optional[int] = None) -> str:
        """Summarize text using the configured LLM provider."""
        if not text.strip():
            return ""
        
        if max_length is None:
            max_length = max(50, len(text) // 3)
        
        prompt = f"""
Please summarize the following text concisely in approximately {max_length} characters or less:

{text}

Summary:"""
        
        return self.complete_text(prompt, max_tokens=min(max_length // 2, 500))
    
    async def summarize_text_async(self, text: str, max_length: Optional[int] = None) -> str:
        """Asynchronously summarize text using the configured LLM provider."""
        if not text.strip():
            return ""
        
        if max_length is None:
            max_length = max(50, len(text) // 3)
        
        prompt = f"""
Please summarize the following text concisely in approximately {max_length} characters or less:

{text}

Summary:"""
        
        return await self.complete_text_async(prompt, max_tokens=min(max_length // 2, 500))
    
    def _mock_complete_text(self, prompt: str, **kwargs) -> str:
        """Mock text completion for testing."""
        mock_config = self.config.get("mock", {})
        
        if mock_config.get("enable_deterministic_responses", True):
            # Return a deterministic response based on prompt content
            prompt_lower = prompt.lower()
            if "summarize" in prompt_lower:
                return "This is a mock summary of the provided content."
            elif "diagnose" in prompt_lower or "error" in prompt_lower:
                return "Mock diagnosis: The system appears to be functioning normally."
            elif "analyze" in prompt_lower:
                return "Mock analysis: The data shows normal patterns and trends."
            else:
                return f"Mock response to: {prompt[:50]}..."
        else:
            return "Mock LLM response"
    
    async def _mock_complete_text_async(self, prompt: str, **kwargs) -> str:
        """Mock async text completion for testing."""
        mock_config = self.config.get("mock", {})
        delay_ms = mock_config.get("response_delay_ms", 100)
        
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)  # Convert to seconds
        
        return self._mock_complete_text(prompt, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the LLM client."""
        return {
            "provider": self.provider,
            "client_initialized": self.client is not None or self.provider == "mock",
            "async_client_initialized": self.async_client is not None or self.provider == "mock",
            "config": self._get_provider_config()
        }


# Global client instance
_llm_client = None


def get_llm_client(config_path: Optional[str] = None) -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(config_path)
    return _llm_client


def initialize_llm_client(config_path: Optional[str] = None) -> LLMClient:
    """Initialize and return a new LLM client instance."""
    global _llm_client
    _llm_client = LLMClient(config_path)
    return _llm_client 