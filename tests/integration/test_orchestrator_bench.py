"""Performance benchmarks for Orchestrator dispatch and LLM latency."""

import time
from unittest.mock import AsyncMock

import pytest

from legion.agents.python import EchoAgent
from legion.core.di_container import ILLMClient, container
from legion.orchestrator import Orchestrator


class FastMockLLMClient:
    async def call(self, messages: list, **kwargs) -> str:
        return "fast"

    def get_embedding(self, text: str) -> list[float]:
        return [0.1] * 1536


@pytest.mark.asyncio
async def test_dispatch_throughput_benchmark(benchmark, monkeypatch, tmp_path):
    # Patch DI container to use fast LLM
    original_llm = container.get(ILLMClient)
    container.register_instance(ILLMClient, FastMockLLMClient())
    # Patch post_to_discord to avoid network
    monkeypatch.setattr(EchoAgent, "post_to_discord", AsyncMock(), raising=False)
    orchestrator = Orchestrator()
    agent_name = "echo_agent"
    content = "benchmark message"
    author = "bench"
    timestamp = time.time()

    async def dispatch_once():
        await orchestrator.dispatch_message(
            agent_name=agent_name,
            content=content,
            author=author,
            timestamp=str(timestamp),
        )

    # Benchmark dispatch throughput (calls per second)
    result = benchmark(asyncio_benchmark_wrapper(dispatch_once))
    # Restore DI
    container.register_instance(ILLMClient, original_llm)
    assert result is None  # Just ensure it runs


def asyncio_benchmark_wrapper(async_fn):
    """Wraps an async function for pytest-benchmark."""
    import asyncio

    def runner():
        asyncio.run(async_fn())

    return runner


@pytest.mark.asyncio
async def test_llm_latency_benchmark(benchmark, monkeypatch):
    # Patch DI container to use fast LLM
    original_llm = container.get(ILLMClient)
    container.register_instance(ILLMClient, FastMockLLMClient())
    orchestrator = Orchestrator()
    agent = orchestrator.agents["echo_agent"]
    # Patch post_to_discord
    monkeypatch.setattr(EchoAgent, "post_to_discord", AsyncMock(), raising=False)
    thread_id = "bench"
    messages = [{"role": "user", "content": "hi"}]
    # Benchmark LLM call
    result = benchmark(lambda: asyncio_run(agent.llm.call(messages)))
    # Restore DI
    container.register_instance(ILLMClient, original_llm)
    assert result == "fast"


def asyncio_run(coro):
    import asyncio

    return asyncio.get_event_loop().run_until_complete(coro)
