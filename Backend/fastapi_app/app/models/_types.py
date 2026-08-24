"""Shared column-type helpers so every model builds its enum/UUID columns
the same way instead of repeating the same SQLAlchemy incantations.
"""

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID


def pg_enum(python_enum, pg_type_name: str) -> SAEnum:
    """An Enum column bound to a Postgres type Prisma already created.

    create_type=False is the important part: SQLAlchemy must never try to
    CREATE TYPE itself, since Prisma's migration already owns that.
    """
    return SAEnum(
        python_enum,
        name=pg_type_name,
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
        create_type=False,
    )


def uuid_column():
    return PGUUID(as_uuid=True)
