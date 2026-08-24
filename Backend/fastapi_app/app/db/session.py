"""Async SQLAlchemy engine/session wiring.

Engine creation is lazy (only happens when get_engine() is first called) so
importing this module — or booting the FastAPI app — never fails just
because POSTGRESQL_DATABASE_URL isn't configured yet or the database is
unreachable. Only code paths that actually touch the database raise.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.errors import ResumindError

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


class DatabaseNotConfiguredError(ResumindError):
    status_code = 503
    error_code = "database_not_configured"


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        if not settings.sqlalchemy_database_url:
            raise DatabaseNotConfiguredError(
                "POSTGRESQL_DATABASE_URL is not set. Add your Neon connection "
                "string to Backend/.env."
            )
        # Neon requires SSL; asyncpg needs it passed via connect_args rather
        # than the sslmode= query param Prisma's URL ships with (see
        # Settings.sqlalchemy_database_url).
        _engine = create_async_engine(
            settings.sqlalchemy_database_url,
            connect_args={"ssl": "require", "timeout": 10},
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(), expire_on_commit=False
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: `db: AsyncSession = Depends(get_db)`."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
