import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import pg_enum, uuid_column
from app.models.enums import ImportanceLevel, RequirementType


class Requirement(Base):
    """A single extracted requirement, sourced from a JD and/or a target
    profile (spec §11-13). Both source FKs are nullable — at least one is
    expected to be set; enforced in application code, not a DB constraint,
    for now."""

    __tablename__ = "requirements"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    job_description_id: Mapped[uuid.UUID | None] = mapped_column(
        uuid_column(), ForeignKey("job_descriptions.id", ondelete="CASCADE")
    )
    target_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        uuid_column(), ForeignKey("target_profiles.id", ondelete="CASCADE")
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[RequirementType] = mapped_column(pg_enum(RequirementType, "requirement_type"), nullable=False)
    canonical_entity: Mapped[str | None] = mapped_column(String)
    importance: Mapped[ImportanceLevel] = mapped_column(
        pg_enum(ImportanceLevel, "importance_level"), default=ImportanceLevel.UNKNOWN
    )
    critical: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float | None] = mapped_column(Float)
    source_section: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job_description: Mapped["JobDescription"] = relationship(back_populates="requirements")
    target_profile: Mapped["TargetProfile"] = relationship(back_populates="requirements")
    matches: Mapped[list["RequirementMatch"]] = relationship(back_populates="requirement")
