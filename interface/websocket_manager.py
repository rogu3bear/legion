"""WebSocket Connection Manager."""

import logging
from typing import Any, List

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # TODO: Add support for rooms/topics if needed later
        # self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"WebSocket client connected. Total: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket client disconnected. Total: {len(self.active_connections)}"
            )
        else:
            logger.warning("Attempted to disconnect an unknown WebSocket client.")

    async def send_personal_message(self, message: Any, websocket: WebSocket):
        """Sends a message to a specific WebSocket client."""
        try:
            await websocket.send_json(message)  # Send JSON by default
        except WebSocketDisconnect:
            logger.warning(
                "Attempted to send to a disconnected client (personal message)."
            )
            self.disconnect(websocket)
        except Exception:
            logger.exception("Error sending personal message to WebSocket client")
            self.disconnect(websocket)  # Assume connection is broken

    async def broadcast(self, message: Any):
        """Broadcasts a message to all active connections."""
        # Create a list of connections to iterate over, as disconnects might modify the original list
        connections_to_send = list(self.active_connections)
        disconnected_clients = []

        for connection in connections_to_send:
            try:
                await connection.send_json(message)  # Send JSON by default
            except WebSocketDisconnect:
                logger.info("Client disconnected during broadcast.")
                disconnected_clients.append(connection)
            except Exception:
                logger.exception("Error sending broadcast message to WebSocket client")
                disconnected_clients.append(connection)  # Assume connection is broken

        # Clean up any clients that disconnected during broadcast
        for client in disconnected_clients:
            self.disconnect(client)


# Global instance of the manager
# This can be imported and used throughout the application
manager = ConnectionManager()
