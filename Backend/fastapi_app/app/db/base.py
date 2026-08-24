"""SQLAlchemy declarative base.

All models in app/models import Base from here so Base.metadata sees every
table (used by tests to introspect/validate the schema).

Prisma (Backend/prisma/schema.prisma) is the migration authority for this
database — these models describe the same tables for querying from FastAPI,
they do not generate or run migrations themselves.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
