"""Configuration and settings for middleware service"""
import os
try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TOKEN: str
    CHROMA_API_URL: str
    CHROMA_API_KEY: str
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp/prom"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 