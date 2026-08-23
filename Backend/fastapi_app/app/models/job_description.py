import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._types import pg_enum, uuid_column
from app.models.enums import DocumentSourceType


class JobDescription(Base):
    """A job description supplied as PDF or pasted text (spec §10)."""

    __tablename__ = "job_descriptions"

    id: Mapped[uuid.UUID] = mapped_column(uuid_column(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(uuid_column(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str | None] = mapped_column(String)
    company: Mapped[str | None] = mapped_column(String)
    source_type: Mapped[DocumentSourceType] = mapped_column(
        pg_enum(DocumentSourceType, "document_source_type"), default=DocumentSourceType.TEXT
    )
    source_filename: Mapped[str | None] = mapped_column(String)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[dict | None] = mapped_column(JSONB)
    parser_version: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="job_descriptions")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="job_description")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="job_description")
