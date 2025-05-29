"""
API v1 endpoints package - minimal stub routers for UI startup.
"""

from fastapi import APIRouter

# Create minimal stub routers to bypass import issues
agents_router = APIRouter()
auth_router = APIRouter()
login_router = APIRouter()
memory_router = APIRouter()
echo_router = APIRouter()
system_router = APIRouter()
task_registry_router = APIRouter()
tasks_router = APIRouter()
lmstudio_proxy_router = APIRouter()
queue_router = APIRouter()
prompt_router = APIRouter()
metrics_router = APIRouter()
agent_router = APIRouter()
middleware_router = APIRouter()
handshake_bp = APIRouter()

# Add basic health endpoints to each router
@agents_router.get("/health")
def agents_health():
    return {"status": "ok", "service": "agents"}

@auth_router.get("/health")
def auth_health():
    return {"status": "ok", "service": "auth"}

@login_router.get("/health")
def login_health():
    return {"status": "ok", "service": "login"}

@memory_router.get("/health")
def memory_health():
    return {"status": "ok", "service": "memory"}

@echo_router.get("/health")
def echo_health():
    return {"status": "ok", "service": "echo"}

@system_router.get("/health")
def system_health():
    return {"status": "ok", "service": "system"}

@task_registry_router.get("/health")
def task_registry_health():
    return {"status": "ok", "service": "task_registry"}

@tasks_router.get("/health")
def tasks_health():
    return {"status": "ok", "service": "tasks"}

@lmstudio_proxy_router.get("/health")
def lmstudio_proxy_health():
    return {"status": "ok", "service": "lmstudio_proxy"}

@queue_router.get("/health")
def queue_health():
    return {"status": "ok", "service": "queue"}

@prompt_router.get("/health")
def prompt_health():
    return {"status": "ok", "service": "prompt"}

@metrics_router.get("/health")
def metrics_health():
    return {"status": "ok", "service": "metrics"}

@agent_router.get("/health")
def agent_health():
    return {"status": "ok", "service": "agent"}

@middleware_router.get("/health")
def middleware_health():
    return {"status": "ok", "service": "middleware"}

@handshake_bp.get("/health")
def handshake_health():
    return {"status": "ok", "service": "handshake"}

__all__ = [
    "agents_router",
    "auth_router",
    "prompt_router",
    "lmstudio_proxy_router",
    "login_router",
    "memory_router",
    "system_router",
    "tasks_router",
    "task_registry_router",
    "echo_router",
    "queue_router",
    "metrics_router",
    "agent_router",
    "middleware_router",
    "handshake_bp",
]
