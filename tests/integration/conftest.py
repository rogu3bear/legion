import asyncio
import inspect
from unittest.mock import MagicMock

import pytest
import yaml

from core.di_container import ILLMClient, IStateManager, container
from core.state import StateManager
from legion.agents.python import EchoAgent  # Ensure EchoAgent is importable
from legion.orchestrator import Orchestrator


# Mock LLM Client (adapted from test_orchestrator_dispatch.py)
class MockLLMClient:
    def __init__(self):
        self.model = "mock_model"
        self.default_kwargs = {"temperature": 0.5, "max_tokens": 100}
        self.client = MagicMock()
        self.client.embeddings = MagicMock()
        mock_embedding_data = MagicMock()
        mock_embedding_data.embedding = [0.1, 0.2] * 768
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [mock_embedding_data]
        self.client.embeddings.create.return_value = mock_embedding_response

        self.client.chat = MagicMock()
        self.client.chat.completions = MagicMock()
        mock_chat_choice = MagicMock()
        mock_chat_choice.message = MagicMock()
        mock_chat_choice.message.content = "Mock LLM Response from conftest"
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [mock_chat_choice]
        self.client.chat.completions.create.return_value = mock_chat_response

    async def call(self, messages: list, **kwargs) -> str:
        # This method might not be directly used by BaseAgent.call_llm if it uses .client directly
        return "Mock LLM Response from MockLLMClient.call (conftest)"

    def get_embedding(self, text: str) -> list[float]:
        # This method might not be directly used by BaseAgent.get_message_embedding if it uses .client directly
        response = self.client.embeddings.create(
            input=[text], model="mock-embedding-model"
        )
        return response.data[0].embedding


@pytest.fixture
def mock_llm_client_instance():
    return MockLLMClient()


@pytest.fixture
def state_manager_instance(tmp_path):
    state_dir = tmp_path / "test_state"
    state_dir.mkdir()
    return StateManager(state_dir=str(state_dir))


@pytest.fixture(autouse=True)
def setup_di_container(state_manager_instance, mock_llm_client_instance):
    """Automatically registers mock instances in the DI container for integration tests."""
    original_state_manager = None
    original_llm_client = None

    try:
        original_state_manager = container.get(IStateManager)
    except KeyError:
        pass  # Not registered, fine

    try:
        original_llm_client = container.get(ILLMClient)
    except KeyError:
        pass  # Not registered, fine

    container.register_instance(IStateManager, state_manager_instance)
    container.register_instance(ILLMClient, mock_llm_client_instance)

    yield

    # Teardown: Restore original or clear
    if original_state_manager:
        container.register_instance(IStateManager, original_state_manager)
    else:
        # If it wasn't there before, remove our mock or re-register factory if that's desired
        # For simplicity, we can try to remove it. DIContainer needs a .unregister or .pop method.
        # Since it doesn't have one, we might need to rely on container.clear() if used between test modules,
        # or re-register the default factory if we know it.
        # For now, let's assume if it wasn't there, it means the default factory should be active.
        # The default factory is registered at the end of di_container.py
        # A more robust DI would have unregister. For now, pop from internal dict if possible or clear.
        if IStateManager in container._instances:  # Accessing internal for cleanup
            del container._instances[IStateManager]
        # Re-register default factory if it was overwritten and not present before
        # from core.state import StateManager # Ensure import
        # container.register_factory(IStateManager, StateManager)

    if original_llm_client:
        container.register_instance(ILLMClient, original_llm_client)
    else:
        if ILLMClient in container._instances:
            del container._instances[ILLMClient]
        # from legion.core.llm_client import LLMClient # Ensure import
        # container.register_factory(ILLMClient, LLMClient)

    # A simpler teardown might be to re-register the default factories if nothing was there before.
    # This depends on the desired isolation. Popping the instance is cleaner if no default should exist.
    # If default factories are always expected if no instance, then re-register factory.
    # Current DI registers default factories at import time.
    # If the original was None, it means the factory was active. Removing instance reverts to factory.
    # So, just deleting the instance should be enough if factory lookups are live.


@pytest.fixture
def minimal_agent_config(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    echo_config_file = config_dir / "echo.yaml"

    echo_config_content = {
        "name": "echo",
        "class": "EchoAgent",  # Ensure this matches a key in CLASS_MAP or is auto-discoverable
        "prompt": "You are an echo agent.",
        "channel_id": "test_channel_echo",
    }
    with open(echo_config_file, "w") as f:
        yaml.dump({"agents": [echo_config_content]}, f)

    return str(config_dir)


@pytest.fixture
async def orchestrator(
    minimal_agent_config, setup_di_container
):  # setup_di_container ensures mocks are set
    """Provides an Orchestrator instance with minimal config and mocked dependencies."""
    from legion.orchestrator import (
        CLASS_MAP as ORCH_CLASS_MAP,  # get the orchestrator's map
    )

    if "EchoAgent" not in ORCH_CLASS_MAP:
        ORCH_CLASS_MAP["EchoAgent"] = EchoAgent

    # Orchestrator.__init__ starts background tasks.
    # This should now happen within the event loop provided to this async fixture.
    orch = Orchestrator()

    echo_config = {
        "name": "echo",
        "class": "EchoAgent",
        "prompt": "You are an echo agent.",
        "channel_id": "123456789",
    }
    orch.config = {"echo": echo_config}  # Override loaded configs for simplicity
    orch.agent_channel_ids = {
        "echo": "123456789"
    }  # Ensure channel_id is string if Discord expects it

    if "echo" not in orch.agents:  # Manually add if not loaded by simplified config
        echo_agent = EchoAgent(
            name="echo",
            config=echo_config,
            orchestrator_ref=orch,
            llm_client=container.get(
                ILLMClient
            ),  # LLM client already mocked by setup_di_container
        )
        orch.agents["echo"] = echo_agent

    yield orch

    # Teardown: Cancel background tasks
    # Helper to get task name for logging
    def task_name(task_item):  # Renamed task to task_item to avoid conflict
        try:
            return task_item.get_name()
        except Exception:
            return str(task_item)

    if hasattr(orch, "_background_tasks") and orch._background_tasks:
        tasks_to_cancel = list(orch._background_tasks)  # Iterate over a copy
        if tasks_to_cancel:
            print(
                f"Fixture teardown: Cancelling {len(tasks_to_cancel)} orchestrator background tasks..."
            )
            for task_item in tasks_to_cancel:  # Renamed task to task_item
                if not task_item.done():
                    task_item.cancel()
                    try:
                        await task_item  # Allow task to process cancellation
                    except asyncio.CancelledError:
                        print(f"Task {task_name(task_item)} was cancelled.")
                    except Exception as e:
                        print(
                            f"Exception during task {task_name(task_item)} cancellation: {e}"
                        )
            # Ensure all tasks are indeed processed after cancellation attempt
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            print("Fixture teardown: Finished processing task cancellations.")

    # If Orchestrator has explicit stop/close methods for ZMQ, call them here.
    if hasattr(orch, "stop_zmq_servers") and inspect.iscoroutinefunction(
        orch.stop_zmq_servers
    ):
        await orch.stop_zmq_servers()
    elif hasattr(orch, "stop_zmq_servers"):
        orch.stop_zmq_servers()


@pytest.fixture
def agent_keys():
    """Provides a list of expected agent keys for tests like agent_roundtrip."""
    # These should correspond to agents typically loaded by default
    # or by the minimal_agent_config if that's what orchestrator uses.
    # The orchestrator fixture currently loads only 'echo'.
    # If other tests expect more, this needs to be dynamic or comprehensive.
    # For test_agent_roundtrip, it might iterate these.
    # Let's assume the `orchestrator` fixture ensures these are available.
    return ["echo"]  # For now, align with what orchestrator fixture sets up.
    # return ["architect", "metrics", "ux_designer", "therapist", "ping", "echo", "healthcheck"]
