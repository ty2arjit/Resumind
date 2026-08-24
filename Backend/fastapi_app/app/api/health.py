"""Health check — proves the app boots and (optionally) that the database
is reachable. Other entity routers (resumes, jobs, analysis, target
profiles — spec §47) get added under app/api/ as each module is built;
none of that logic exists yet, so nothing else is mounted in Phase 1.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    """Raises (via the centralized error handlers in app.core.errors) with
    a clear code if POSTGRESQL_DATABASE_URL is unset or Neon is
    unreachable, instead of returning a misleading 200."""
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
