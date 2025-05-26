from fastapi import APIRouter

from .endpoints import agents, auth, login, memory, system, tasks, lmstudio_health, prompts, lmstudio_proxy

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(lmstudio_health.router, prefix="/health", tags=["lmstudio"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(lmstudio_proxy.router, prefix="/lmstudio", tags=["lmstudio-proxy"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
