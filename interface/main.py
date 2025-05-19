import sys # sys must be imported first for path modifications
from pathlib import Path # pathlib for path manipulations

# Ensure the project root directory is in the Python path very early.
# This must be done before any other imports that might rely on this path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Standard library imports
import asyncio
import json
# import os # No longer needed for os.path

# Third-party imports
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Project-specific imports
from legion.core.logging_config import setup_logging
from legion import Orchestrator
from interface.orchestrator_comm import send_request

logger = setup_logging(__name__)

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include API routers
from interface.api.v1.endpoints import (  # noqa: E402
    agents_router,
    auth_router,
    login_router,
    memory_router,
    system_router,
    task_registry_router,
    tasks_router,
    lmstudio_proxy_router,
    queue_router,
)
from interface.internal.diagnostics import router as diagnostics_router
from interface.internal.capabilities import router as capabilities_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(login_router, prefix="/api/v1/login", tags=["login"])
app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(system_router, prefix="/api/v1/system", tags=["system"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(task_registry_router, prefix="/api/v1/registry/tasks", tags=["registry_tasks"])
app.include_router(queue_router, prefix="/api/v1", tags=["queue"])
app.include_router(memory_router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(lmstudio_proxy_router, prefix="/api/v1/lmstudio", tags=["lmstudio"])
app.include_router(diagnostics_router, prefix="/internal", tags=["internal"])
app.include_router(capabilities_router, prefix="/internal", tags=["internal"])

# WebSocket connections manager (simple list for now)
active_connections: list[WebSocket] = []


# Create database tables on startup
@app.on_event("startup")
def on_startup():
    # Import Base and engine to initialize tables
    from interface.db.base import Base, engine

    Base.metadata.create_all(bind=engine)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        # Only set HSTS if running under HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Renders the main feed HTML page."""
    return templates.TemplateResponse("feed.html", {"request": request})


@app.get("/api/feed")
def get_feed():
    """Returns the latest events from the orchestrator as JSON."""
    events = Orchestrator().run_once()
    return JSONResponse(events[-20:] if len(events) > 20 else events)


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """Sends orchestrator events to the client via websocket."""
    await websocket.accept()
    try:
        while True:
            events = Orchestrator().run_once()
            await websocket.send_text(json.dumps(events[-1] if events else {}))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass


@app.get("/")
def root():
    return {"message": "Legion Interface Stub"}


@app.get("/status")
def health_status():
    """Simple healthcheck returning orchestrator uptime and agents."""
    resp = send_request({"action": "status"})
    if not resp or "response" not in resp:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": "Orchestrator unavailable"},
        )
    data = resp["response"]
    return {
        "status": "ok",
        "uptime": data.get("uptime", 0),
        "agents": data.get("active_agents", []),
    }


async def send_to_all(message: str):
    """Sends a message to all connected WebSocket clients."""
    logger.debug(
        f"Broadcasting message to {len(active_connections)} clients",
        extra={
            "message_content": message[:50] + "..." if len(message) > 50 else message
        },
    )
    disconnected_clients = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except WebSocketDisconnect:
            logger.info("Client disconnected during broadcast.")
            disconnected_clients.append(connection)
        except Exception as e:
            logger.error("Error sending message to WebSocket client", exc_info=e)
            disconnected_clients.append(connection)
    # Clean up disconnected clients
    for client in disconnected_clients:
        active_connections.remove(client)


@app.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    """WebSocket endpoint for the live feed."""
    logger.info("WebSocket client connected to feed.")
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep connection alive, potentially receive commands
            data = await websocket.receive_text()
            logger.debug(f"Received command from WebSocket: {data}")
            # Process commands if needed (e.g., filter feed)
            # For now, just echo back or log
            await websocket.send_text(f"Echo: {data}")  # Example echo

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected gracefully.")
    except Exception as e:
        logger.exception("WebSocket error", exc_info=e)
    finally:
        logger.info("Removing client from active connections.")
        active_connections.remove(websocket)


async def push_updates():
    """Example background task to simulate pushing feed updates."""
    count = 0
    logger.info("Starting background update task.")
    while True:
        await asyncio.sleep(5)  # Simulate delay
        count += 1
