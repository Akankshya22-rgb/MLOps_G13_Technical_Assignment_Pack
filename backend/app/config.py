from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Anchored to the backend/ directory (not the process cwd) so the default SQLite file
# lands in the same place whether the app is started from backend/ or the repo root.
BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_URL = f"sqlite:///{(BACKEND_DIR / 'mlops.db').as_posix()}"


class Settings(BaseSettings):
    """Application configuration, sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MLOps Platform API"
    environment: str = "development"
    database_url: str = DEFAULT_SQLITE_URL
    cors_origins: str = "http://localhost:4200"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
