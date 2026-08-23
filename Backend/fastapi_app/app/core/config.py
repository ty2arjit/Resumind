"""Centralized application configuration.

Single source of truth for environment-driven settings. Nothing else in
the codebase should call `os.getenv` directly for these values — import
`get_settings()` instead so configuration stays in one place.
"""

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend/.env is shared across the Node and Python services (matches the
# existing project convention — see Backend/config/db.js on the Node side).
_BACKEND_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"

    # Same Neon connection string Prisma uses (Backend/.env: POSTGRESQL_DATABASE_URL).
    # SQLAlchemy's asyncpg driver needs a "postgresql+asyncpg://" scheme, which
    # differs from the plain "postgresql://" Prisma expects — converted below so
    # only one URL has to be configured.
    postgresql_database_url: str | None = None

    gemini_api_key: str | None = None

    # Phase 5 — local pretrained embedding model (spec §12: "Keep the
    # selected model configurable. Do not hard-code the model name
    # throughout the application").
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    @property
    def sqlalchemy_database_url(self) -> str | None:
        """Same connection string Prisma uses, adapted for SQLAlchemy + asyncpg.

        asyncpg does not understand libpq-style query params (`sslmode`,
        `channel_binding`) that Neon's connection string ships with — SSL is
        configured separately via `connect_args` in db/session.py instead,
        so the query string is dropped here rather than passed through.
        """
        if not self.postgresql_database_url:
            return None
        parts = urlsplit(self.postgresql_database_url)
        scheme = "postgresql+asyncpg"
        return urlunsplit((scheme, parts.netloc, parts.path, "", ""))


@lru_cache
def get_settings() -> Settings:
    return Settings()
