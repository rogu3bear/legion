#!/usr/bin/env python3
"""
Stub LLM client for integration testing.
Returns a simple dict echoing the input prompt.
"""

from typing import Any, Dict


class StubLLMClient:
    """A fake LLM client that echoes prompts in a dict with status."""

    def create(self, payload: Any) -> Dict[str, Any]:
        """
        Simulate an LLM create call by returning status ok and echoing payload.
        Args:
            payload: The input payload (prompt or message)
        Returns:
            A dict containing `status: "ok"` and the original payload under `echo`.
        """
        return {"status": "ok", "echo": payload}
