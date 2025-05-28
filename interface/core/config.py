"""Core application settings."""

import os

from pydantic_settings import BaseSettings

from legion.ports import get_port


class Settings(BaseSettings):
    PROJECT_NAME: str = "Legion Interface"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./test.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list = [
        f"http://localhost:{os.getenv('FRONTEND_PORT', '7602')}",
        f"http://localhost:{os.getenv('LEGION_API_PORT', '7601')}",
    ]

    ORCHESTRATOR_ADDRESS: str = f"tcp://localhost:{get_port('orchestrator')}"

    class Config:
        case_sensitive = True


settings = Settings()
