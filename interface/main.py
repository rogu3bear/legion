"""Legion interface FastAPI app stub."""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from legion.orchestrator import Orchestrator

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


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
