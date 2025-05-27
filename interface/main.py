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
import os # No longer needed for os.path

# Third-party imports
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Project-specific imports
from legion.core.logging_config import setup_logging
# from legion import Orchestrator  # TEMPORARILY DISABLED FOR UI AUDIT

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
    echo_router,
    system_router,
    task_registry_router,
    tasks_router,
    lmstudio_proxy_router,
    queue_router,
    prompt_router,
    metrics_router,
    middleware_router,
)

# Import RedirectResponse for 301 redirects
from fastapi.responses import RedirectResponse

# Router guards - ensure all routers are properly initialized
from fastapi.routing import APIRouter
assert isinstance(auth_router, APIRouter), f"auth_router is {type(auth_router)}, expected APIRouter"
assert isinstance(login_router, APIRouter), f"login_router is {type(login_router)}, expected APIRouter"
assert isinstance(agents_router, APIRouter), f"agents_router is {type(agents_router)}, expected APIRouter"
assert isinstance(system_router, APIRouter), f"system_router is {type(system_router)}, expected APIRouter"
assert isinstance(tasks_router, APIRouter), f"tasks_router is {type(tasks_router)}, expected APIRouter"
assert isinstance(task_registry_router, APIRouter), f"task_registry_router is {type(task_registry_router)}, expected APIRouter"
assert isinstance(queue_router, APIRouter), f"queue_router is {type(queue_router)}, expected APIRouter"
assert isinstance(memory_router, APIRouter), f"memory_router is {type(memory_router)}, expected APIRouter"
assert isinstance(lmstudio_proxy_router, APIRouter), f"lmstudio_proxy_router is {type(lmstudio_proxy_router)}, expected APIRouter"
assert isinstance(echo_router, APIRouter), f"echo_router is {type(echo_router)}, expected APIRouter"
assert isinstance(prompt_router, APIRouter), f"prompt_router is {type(prompt_router)}, expected APIRouter"
assert isinstance(metrics_router, APIRouter), f"metrics_router is {type(metrics_router)}, expected APIRouter"
assert isinstance(middleware_router, APIRouter), f"middleware_router is {type(middleware_router)}, expected APIRouter"

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(login_router, prefix="/api/v1/login", tags=["login"])
app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(system_router, prefix="/api/v1/system", tags=["system"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(task_registry_router, prefix="/api/v1/registry/tasks", tags=["registry_tasks"])
app.include_router(queue_router, prefix="/api/v1", tags=["queue"])
app.include_router(memory_router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(lmstudio_proxy_router, prefix="/api/v1/lmstudio", tags=["lmstudio"])
app.include_router(prompt_router, prefix="/api/v1", tags=["prompts"])
app.include_router(echo_router, prefix="/api/v1/echo", tags=["echo"])
app.include_router(metrics_router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(middleware_router, prefix="/api/v1/middleware", tags=["middleware"])

# Legacy redirect: /nexus/ → /log/ (301 permanent redirect)
@app.get("/nexus/{path:path}")
def redirect_nexus_to_log(path: str):
    """301 redirect from legacy /nexus/ paths to /log/ paths."""
    return RedirectResponse(url=f"/log/{path}", status_code=301)

@app.get("/nexus")
def redirect_nexus_root_to_log():
    """301 redirect from legacy /nexus root to /log root."""
    return RedirectResponse(url="/log", status_code=301)

# WebSocket connections manager (simple list for now)
active_connections: list[WebSocket] = []


# Create database tables on startup - TEMPORARILY DISABLED DUE TO SYNTAX ERRORS
# @app.on_event("startup")
# def on_startup():
#     # Import Base and engine to initialize tables
#     from interface.db.base import Base, engine

#     try:
#         import redis  # type: ignore
#     except Exception:
#         redis = None

#     from legion.core.state import restore_agent_state_from_redis

#     Base.metadata.create_all(bind=engine)

#     if redis is not None:
#         try:
#             r = redis.Redis(host="localhost", port=int(os.getenv("REDIS_PORT", 7600)), decode_responses=True)
#             recovered = restore_agent_state_from_redis(r)
#             logger.info(
#                 "Recovered %d agent(s) from Redis", len(recovered)
#             )
#         except Exception as exc:  # pragma: no cover - startup logging only
#             logger.error("Failed to restore agents from Redis: %s", exc)


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
    """Renders the main Legion dashboard HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/feed")
def get_feed():
    """Returns sample events for UI testing."""
    # Simplified for UI audit - normally gets events from Orchestrator
    sample_events = [
        {"timestamp": "2025-05-28T16:00:00Z", "type": "agent_status", "agent": "echo", "status": "active"},
        {"timestamp": "2025-05-28T16:01:00Z", "type": "task_created", "task_id": "123", "agent": "therapist"},
    ]
    return JSONResponse(sample_events)


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """Sends sample events to the client via websocket for UI testing."""
    await websocket.accept()
    try:
        while True:
            # Sample event for UI testing
            sample_event = {"timestamp": "2025-05-28T16:00:00Z", "type": "heartbeat", "status": "ok"}
            await websocket.send_text(json.dumps(sample_event))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


async def send_to_all(message: str):
    """Sends a message to all connected WebSocket clients."""
    logger.debug(
        f"Broadcasting message to {len(active_connections)} clients",
        extra={
            "message_content": message[:50] + "..." if len(message) > 50 else message
        }
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
        await send_to_all(f"Update {count}")
