"""Configuration and settings for middleware service"""

try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings

from legion.ports import get_chroma_url


class Settings(BaseSettings):
    API_TOKEN: str
    CHROMA_API_URL: str = get_chroma_url()
    CHROMA_API_KEY: str
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp/prom"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
