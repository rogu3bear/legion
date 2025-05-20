import asyncio
import json
import logging
from unittest.mock import AsyncMock, patch

import pytest
import zmq.asyncio
from legion.core.di_container import ILLMClient, IStateManager, container
from legion.orchestrator import Orchestrator

# Configure logging for tests (optional, but can be helpful for debugging)
# from legion.utils.logging import setup_legion_logging
# setup_legion_logging(log_level_str='DEBUG', log_to_console=True) # Use console for test output


class MockAgent:
    def __init__(
        self, name="test_agent", config=None, orchestrator_ref=None, llm_client=None
    ):
        self.name = name
        self.config = config or {}
        self.orchestrator_ref = orchestrator_ref
        self.llm_client = llm_client
        self._is_shutdown = False

    async def handle_task(self, payload):
        if payload.get("action") == "raise_exception":
            raise ValueError("Test agent exception")
        return f"Response from {self.name} for: {payload.get('content')}"

    async def shutdown(self):
        logging.info(f"MockAgent {self.name} shutdown called.")
        self._is_shutdown = True

    def is_shutdown(self):
        return self._is_shutdown


@pytest.fixture
async def mock_dependencies():
    container.clear()

    mock_state_manager = AsyncMock(spec=IStateManager)

    # Create a mock for the agent memory object
    mock_agent_memory_instance = AsyncMock(name="MockAgentMemoryInstance")
    mock_agent_memory_instance.log_interaction = AsyncMock(
        name="MockLogInteraction"
    )  # Add log_interaction mock

    # Configure get_agent_memory to return our detailed mock_agent_memory_instance
    mock_state_manager.get_agent_memory = AsyncMock(
        return_value=mock_agent_memory_instance
    )

    mock_llm_client = AsyncMock(spec=ILLMClient)

    container.register_factory(IStateManager, lambda: mock_state_manager)
    container.register_factory(ILLMClient, lambda: mock_llm_client)

    yield mock_state_manager, mock_llm_client

    # Clean up: Clear all registrations after the test session part that used these mocks
    # This helps prevent interference with other tests if the container is truly global
    # and not reset elsewhere.
    container.clear()
    # Re-register default services if they are needed by other tests not using this fixture
    # This is important if the test runner doesn't isolate DI container state between test files/sessions.
    # For simplicity here, we assume tests either all mock or this clear is acceptable.
    # A more robust global setup/teardown for DI might be needed for larger test suites.
    # Re-registering defaults:
    from legion.core.llm_client import LLMClient as DefaultLLMClient
    from legion.core.state import StateManager as DefaultStateManager

    container.register_factory(ILLMClient, DefaultLLMClient)
    container.register_factory(IStateManager, DefaultStateManager)


@pytest.fixture
async def orchestrator_instance(mock_dependencies):
    mock_state_manager, mock_llm_client = mock_dependencies

    mock_agent_configs_dict = {
        "test_agent": {
            "name": "test_agent",
            "class": "MockAgent",
            "prompt": "test_prompt",
            "channel_id": "12345",
            # Ensure all fields accessed by agent instantiation in Orchestrator.__init__ are present
            # e.g., if it accesses config.get("memory_base_dir") for LegionAgentMemory
        },
        "error_agent": {
            "name": "error_agent",
            "class": "MockAgent",
            "prompt": "error_prompt",
            "channel_id": "67890",
        },
    }

    # This side effect function will be called when Orchestrator.load_agent_configs() is invoked.
    # 'self_orch' will be the instance of the Orchestrator.
    def mock_load_agent_configs_side_effect(self_orch_param):
        self_orch_param.config = mock_agent_configs_dict
        return mock_agent_configs_dict

    # Patch Orchestrator.load_agent_configs to use our side effect.
    # Patch CLASS_MAP in the orchestrator module to include MockAgent.
    with patch.object(
        Orchestrator,
        "load_agent_configs",
        side_effect=mock_load_agent_configs_side_effect,
        autospec=True,
    ), patch("legion.orchestrator.CLASS_MAP", {"MockAgent": MockAgent}):
        # Initialize orchestrator. Inside __init__, our patched load_agent_configs will run,
        # setting self.config. Then, the agent instantiation loop will run using this
        # self.config and the patched CLASS_MAP.
        orch = Orchestrator(
            state_manager=mock_state_manager, llm_client=mock_llm_client, pid_file=None
        )

        # Verification: Ensure agents were loaded by __init__ based on the mocked config and CLASS_MAP
        assert "test_agent" in orch.agents
        assert isinstance(orch.agents["test_agent"], MockAgent)
        assert "error_agent" in orch.agents
        assert isinstance(orch.agents["error_agent"], MockAgent)
        # _agent_instances is an old pattern, self.agents is primary
        assert orch._agent_instances == orch.agents

    yield orch

    # Shutdown orchestrator and its tasks
    logging.info("Starting orchestrator shutdown in test fixture...")
    await orch.shutdown()
    logging.info("Orchestrator shutdown in test fixture complete.")

    # Ensure all background tasks created by orchestrator are awaited/cancelled
    # This is critical to avoid warnings like "Task was destroyed but it is pending!"
    # Orchestrator's shutdown should handle its _background_tasks (ZMQ loops)
    # If other tasks are created directly in tests or by Orchestrator outside _background_tasks,
    # they might need explicit handling here or in the Orchestrator's shutdown.
    # Give a very small delay for any final task cleanup if needed.
    await asyncio.sleep(0.01)


@pytest.mark.asyncio
async def test_orchestrator_startup_and_shutdown(orchestrator_instance):
    """Test basic startup and graceful shutdown of the orchestrator."""
    orch = orchestrator_instance
    assert orch is not None
    assert orch.zmq_context is not None
    assert not orch.zmq_context.closed

    # Simulate some activity or just check initial state
    assert "test_agent" in orch.agents

    # Shutdown is handled by the fixture's teardown.
    # We can add assertions here that would be true before explicit shutdown,
    # and then rely on fixture for the shutdown call.
    # For this test, the fixture's yield and subsequent shutdown is the primary test.
    # To be more explicit here (though redundant with fixture):
    await (
        orch.shutdown()
    )  # Call it again to ensure idempotency if designed for it, or just to test call
    assert orch.zmq_context.closed
    assert orch.agents["test_agent"].is_shutdown()  # Check if agent shutdown was called


@pytest.mark.asyncio
async def test_dispatch_message_agent_exception(orchestrator_instance, caplog):
    """Test exception handling when an agent's handle_task raises an error during dispatch_message."""
    orch = orchestrator_instance
    caplog.set_level(logging.ERROR)

    # Patch run_middleware_pipeline to simulate it passing, so we test agent exception
    with patch(
        "legion.orchestrator.run_middleware_pipeline",
        return_value={"final_valid": True, "directive": "trigger error"},
    ) as mock_middleware, patch.object(
        orch.agents["error_agent"],
        "handle_task",
        side_effect=ValueError("Agent task failed badly"),
    ) as mock_handle_task:
        response = await orch.dispatch_message(
            agent_name="error_agent", content="trigger error", author="test_user"
        )

        assert (
            "[Agent 'error_agent' failed to process message: Agent task failed badly]"
            in response
        )
        mock_middleware.assert_called_once()
        mock_handle_task.assert_called_once()

        assert any(
            "Agent 'error_agent' encountered ValueError" in record.message
            and "Agent task failed badly" in record.message
            for record in caplog.records
        )


@pytest.mark.asyncio
async def test_dispatch_message_unknown_agent(orchestrator_instance, caplog):
    """Test dispatch_message with an unknown agent name."""
    orch = orchestrator_instance
    caplog.set_level(logging.ERROR)

    # Patch run_middleware_pipeline to simulate it passing, so we test unknown agent error
    with patch(
        "legion.orchestrator.run_middleware_pipeline",
        return_value={"final_valid": True, "directive": "Hello"},
    ) as mock_middleware:
        response = await orch.dispatch_message(
            agent_name="non_existent_agent", content="Hello", author="test_user"
        )

    assert "Error: Agent 'non_existent_agent' not found" in response
    mock_middleware.assert_called_once()
    assert any(
        "Agent 'non_existent_agent' not found" in record.message
        for record in caplog.records
    )


@pytest.mark.asyncio
async def test_ask_agent_exception(orchestrator_instance, caplog):
    """Test exception handling in the 'ask' method when an agent fails."""
    orch = orchestrator_instance
    caplog.set_level(logging.ERROR)

    with patch.object(
        orch.agents["error_agent"],
        "handle_task",
        side_effect=RuntimeError("Ask failed in agent"),
    ):
        response = await orch.ask(agent_name="error_agent", prompt="problematic prompt")

    assert "Error asking agent 'error_agent': Ask failed in agent" in response
    assert any(
        "Error asking agent 'error_agent'" in record.message
        and "Ask failed in agent" in record.message
        for record in caplog.records
    )


@pytest.mark.asyncio
async def test_broadcast_with_agent_exception(orchestrator_instance, caplog):
    """Test exception handling in the 'broadcast' method when an agent fails."""
    orch = orchestrator_instance
    caplog.set_level(logging.ERROR)

    # Go back to the original strategy of mocking the agent.handle_task methods directly
    # This is more reliable than patching the 'ask' method

    # Create mock implementations for handle_task
    async def mock_success_handle_task(payload):
        return "Success response"

    async def mock_error_handle_task(payload):
        raise RuntimeError("Broadcasting failed")

    # Patch both agents' handle_task methods
    with patch.object(
        orch.agents["test_agent"], "handle_task", side_effect=mock_success_handle_task
    ) as mock_success, patch.object(
        orch.agents["error_agent"], "handle_task", side_effect=mock_error_handle_task
    ) as mock_error:
        # Call the broadcast method
        responses = await orch.broadcast(prompt="broadcast message")

        # Verify both agents were called
        mock_success.assert_called_once()
        mock_error.assert_called_once()

        # Verify success response
        assert responses["test_agent"] == "Success response"

        # Verify error response
        assert "Error asking agent 'error_agent'" in responses["error_agent"]
        assert "Broadcasting failed" in responses["error_agent"]

        # Verify log message
        assert any(
            "Error asking agent 'error_agent'" in record.message
            for record in caplog.records
        )


@pytest.mark.asyncio
async def test_zmq_rep_loop_json_decode_error(orchestrator_instance, caplog):
    """Test _zmq_rep_loop handling of JSONDecodeError."""
    orch = orchestrator_instance
    caplog.set_level(logging.ERROR)

    # This test is a bit complex because _zmq_rep_loop runs in a background task.
    # We need to send a malformed message to its socket.
    # Ensure ZMQ REP server is running and socket is available
    if not (
        hasattr(orch, "_zmq_socket")
        and orch._zmq_socket
        and not orch._zmq_socket.closed
    ):
        pytest.skip("ZMQ REP socket not available for testing")

    malformed_json_bytes = b"{this is not json"

    # Create a temporary client socket to send the malformed message
    context = zmq.asyncio.Context.instance()
    client_socket = context.socket(zmq.REQ)

    # Get REP server address (this is tricky as it's usually tcp://*:port)
    # For testing, Orchestrator would need a fixed, known port or a way to report its bound port.
    # Assuming it bound to a known test port or we can retrieve it.
    # Let's assume Orchestrator's ZMQ init methods could store the actual bound address if port was 0.
    # For now, let's skip if we can't easily get the address.
    # This part needs a more robust way to get the ZMQ REP server's actual bind address.
    # A common pattern is to bind to port 0 and then use getsockopt(zmq.LAST_ENDPOINT)
    # The orchestrator would need to expose this.

    # If Orchestrator has _zmq_socket and it has last_endpoint property after bind:
    try:
        rep_server_address = orch._zmq_socket.getsockopt_string(zmq.LAST_ENDPOINT)
        if not rep_server_address:  # Can be empty if not bound yet or other issues
            pytest.skip(
                "Could not determine ZMQ REP server address for client connection."
            )
        client_socket.connect(rep_server_address)
    except zmq.error.ZMQError as e:
        pytest.skip(f"Failed to connect ZMQ REQ client for test: {e}")

    # Send malformed message and expect an error response from the loop's error handling
    try:
        await client_socket.send(malformed_json_bytes)
        # The loop should catch JSONDecodeError, log it, and send an error reply
        error_response_bytes = await client_socket.recv()  # Timeout might be needed
        error_response = json.loads(error_response_bytes.decode())

        assert error_response["status"] == "error"
        assert "Invalid JSON format" in error_response["message"]
        assert any(
            "ZMQ REP: JSON decoding error" in record.message
            for record in caplog.records
        )

    except asyncio.TimeoutError:
        pytest.fail("Timeout waiting for ZMQ REP loop to respond to malformed JSON.")
    except json.JSONDecodeError:
        pytest.fail(
            "Client failed to decode error response, which itself might be malformed."
        )
    finally:
        client_socket.close()


@pytest.mark.asyncio
async def test_zmq_rep_loop_dispatch_command_exception(orchestrator_instance, caplog):
    """Test _zmq_rep_loop handling when dispatch_command raises an exception."""
    orch = orchestrator_instance
    caplog.set_level(logging.ERROR)

    if not (
        hasattr(orch, "_zmq_socket")
        and orch._zmq_socket
        and not orch._zmq_socket.closed
    ):
        pytest.skip("ZMQ REP socket not available for testing")

    # Valid JSON command that will cause dispatch_command to fail
    command_causing_error = {"action": "cause_error_in_dispatch", "payload": {}}

    with patch.object(
        orch,
        "dispatch_command",
        side_effect=Exception("Dispatch command internal error"),
    ) as mock_dispatch:
        context = zmq.asyncio.Context.instance()
        client_socket = context.socket(zmq.REQ)
        try:
            rep_server_address = orch._zmq_socket.getsockopt_string(zmq.LAST_ENDPOINT)
            if not rep_server_address:
                pytest.skip(
                    "Could not determine ZMQ REP server address for client connection."
                )
            client_socket.connect(rep_server_address)

            await client_socket.send_json(command_causing_error)
            response_json = await client_socket.recv_json()  # Timeout might be needed

            mock_dispatch.assert_called_once_with(command_causing_error)
            assert response_json["status"] == "error"
            assert (
                "Error processing command: Dispatch command internal error"
                in response_json["message"]
            )
            assert any(
                "Error dispatching ZMQ command" in record.message
                and "Dispatch command internal error" in record.message
                for record in caplog.records
            )

        except asyncio.TimeoutError:
            pytest.fail(
                "Timeout waiting for ZMQ REP loop response after dispatch_command error."
            )
        finally:
            client_socket.close()


@pytest.mark.asyncio
async def test_middleware_error_handling_in_dispatch_message(
    orchestrator_instance, caplog
):
    """Test dispatch_message when run_middleware_pipeline raises an exception."""
    orch = orchestrator_instance
    caplog.set_level(logging.ERROR)

    # Patch the run_middleware_pipeline function where it's imported in orchestrator.py
    with patch(
        "legion.orchestrator.run_middleware_pipeline",
        side_effect=Exception("Middleware boom!"),
    ) as mock_run_pipeline:
        response = await orch.dispatch_message(
            agent_name="test_agent", content="Test message"
        )

        assert (
            "[Error during incoming middleware processing: Middleware boom!]"
            in response
        )
        mock_run_pipeline.assert_called_once()  # It should be called for 'incoming'
        assert any(
            "Error in incoming middleware" in record.message
            and "Middleware boom!" in record.message
            for record in caplog.records
        )


# Note: Graceful shutdown test is implicitly covered by test_orchestrator_startup_and_shutdown
# and the fixture's teardown. We can add more specific assertions if needed.
# For example, checking if ZMQ loop tasks in _background_tasks were cancelled.


@pytest.mark.asyncio
async def test_shutdown_cancels_background_tasks(orchestrator_instance):
    orch = orchestrator_instance

    # Create a dummy task and add it to background_tasks to simulate an active task
    # Note: Orchestrator's __init__ already starts ZMQ loops and adds them.
    # We rely on those being representative.

    # Get a reference to one of the ZMQ loop tasks if they exist
    # This assumes _zmq_rep_loop or _zmq_pub_loop were started and added to _background_tasks
    initial_bg_tasks = list(orch._background_tasks)  # Make a copy
    assert len(initial_bg_tasks) > 0  # Assuming at least ZMQ loops started

    # Call shutdown (already called by fixture teardown, but can call here for specific check timing)
    await orch.shutdown()

    # Assert that tasks that were in _background_tasks are now cancelled or done
    for task in initial_bg_tasks:
        assert task.done(), f"Task {task} was not done after shutdown."
        if not task.cancelled():  # If not cancelled, it should have completed without error or with logged error
            logging.info(
                f"Task {task} completed with result: {task.result() if not task.exception() else task.exception()}"
            )
        # A stronger check would be that it was indeed cancelled if it was still running
        # or completed cleanly. The shutdown logic aims to cancel them.

    assert orch.zmq_context.closed, "ZMQ context should be closed after shutdown"

    # Check if agent shutdown methods were called
    assert orch.agents["test_agent"].is_shutdown()
    assert orch.agents["error_agent"].is_shutdown()


# Need to import contextlib for the mock_dependencies fixture
