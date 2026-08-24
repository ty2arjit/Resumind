import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import uuid_column


class User(Base):
    """Mirrors the `users` table (see prisma/schema.prisma: model User).

    Auth still runs against MongoDB in Phase 1 — this row is a Postgres-side
    reference point for Resume/Analysis ownership, not yet the system of
    record for login.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    mongo_user_id: Mapped[str | None] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    college: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resumes: Mapped[list["Resume"]] = relationship(back_populates="user")
    job_descriptions: Mapped[list["JobDescription"]] = relationship(back_populates="user")
    target_profiles: Mapped[list["TargetProfile"]] = relationship(back_populates="user")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="user")
