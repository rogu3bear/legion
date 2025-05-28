# tests/test_websockets.py
import asyncio  # Added for sleep

from fastapi.testclient import TestClient

import pytest

# Assuming your main FastAPI app instance is accessible for testing
# If not, you might need a fixture to create it.
# from interface.main import app
# Mock the manager used by the endpoint
# This requires the manager to be accessible or injectable for mocking.
# Alternatively, test the manager class directly in a separate test file.
# Import the manager instance to call broadcast directly
from interface.websocket_manager import manager


@pytest.mark.asyncio
async def test_websocket_connect_disconnect(client: TestClient):
    """Test WebSocket connection and disconnection via /ws/events."""
    try:
        with client.websocket_connect("/ws/events") as websocket:  # Updated path
            assert websocket
            # Send a test message (optional, depends on endpoint handling)
            # await websocket.send_text("Hello from test")
            # data = await websocket.receive_text()
            # assert data == "Echo: Hello from test" # If echo logic exists

            # Context manager handles closing the websocket upon exit
            pass
    except Exception as e:
        pytest.fail(f"WebSocket connection/disconnection failed: {e}")


@pytest.mark.asyncio
async def test_websocket_multiple_connections(client: TestClient):
    """Test handling multiple concurrent WebSocket connections."""
    try:
        with client.websocket_connect("/ws/events") as websocket1:  # Updated path
            with client.websocket_connect("/ws/events") as websocket2:  # Updated path
                assert websocket1
                assert websocket2
                assert len(manager.active_connections) >= 2  # Check manager state
                pass  # Connections established
            # websocket2 disconnects here
            # Give a moment for disconnect to register (though manager handles it)
            await asyncio.sleep(0.01)
            assert len(manager.active_connections) >= 1
            pass  # websocket1 still connected
        # websocket1 disconnects here
        # NOTE: Depending on test setup (if manager is shared across tests)
        # this might not be exactly 0 if other tests ran concurrently.
        # assert len(manager.active_connections) == 0
    except Exception as e:
        pytest.fail(f"Multiple WebSocket connections failed: {e}")


@pytest.mark.asyncio
async def test_websocket_broadcast(client: TestClient):
    """Test broadcasting a message to connected clients."""
    test_message = {"type": "test_broadcast", "data": "hello world"}

    # Need a way to store received messages
    received1 = None
    received2 = None

    try:
        with client.websocket_connect("/ws/events") as websocket1:  # Updated path
            with client.websocket_connect("/ws/events") as websocket2:  # Updated path
                assert len(manager.active_connections) >= 2

                # Directly call the manager's broadcast method
                await manager.broadcast(test_message)

                # Check if messages were received
                # Add timeout to prevent hanging if broadcast fails
                received1 = await asyncio.wait_for(
                    websocket1.receive_json(), timeout=1.0
                )
                received2 = await asyncio.wait_for(
                    websocket2.receive_json(), timeout=1.0
                )

    except Exception as e:
        pytest.fail(f"WebSocket broadcast test failed: {e}")

    assert received1 == test_message
    assert received2 == test_message


# TODO: Add test for the actual background task if feasible (might require more complex mocking)
