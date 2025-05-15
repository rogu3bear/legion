"""Core application settings."""

from pydantic_settings import BaseSettings


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
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    ORCHESTRATOR_ADDRESS: str = "tcp://localhost:5555"

    class Config:
        case_sensitive = True


settings = Settings()
