import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import uuid_column


class TargetProfile(Base):
    """A curated Position + Domain profile (spec §36-38). Most rows are
    expected to be system-seeded (is_system=True); user_id is nullable so
    seed profiles aren't owned by any one account."""

    __tablename__ = "target_profiles"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(uuid_column(), ForeignKey("users.id", ondelete="CASCADE"))
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str | None] = mapped_column(String)
    profile_version: Mapped[str] = mapped_column(String, default="v1")
    profile_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="target_profiles")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="target_profile")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="target_profile")
