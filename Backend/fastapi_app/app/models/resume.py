import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import pg_enum, uuid_column
from app.models.enums import DocumentSourceType


class Resume(Base):
    """A resume the user uploaded. Content lives on ResumeVersion so
    re-uploads are tracked as history (spec §43)."""

    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(uuid_column(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="resumes")
    versions: Mapped[list["ResumeVersion"]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base):
    """One uploaded/parsed snapshot of a resume. `structured_data` is where
    the Phase 2 parser's structured-resume JSON (spec §8.1) will live."""

    __tablename__ = "resume_versions"
    __table_args__ = (UniqueConstraint("resume_id", "version_number"),)

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(uuid_column(), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_filename: Mapped[str | None] = mapped_column(String)
    source_type: Mapped[DocumentSourceType] = mapped_column(
        pg_enum(DocumentSourceType, "document_source_type"), default=DocumentSourceType.PDF
    )
    raw_text: Mapped[str | None] = mapped_column(Text)
    structured_data: Mapped[dict | None] = mapped_column(JSONB)
    parser_version: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="versions")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="resume_version")
