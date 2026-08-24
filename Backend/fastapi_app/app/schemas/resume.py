import uuid
from datetime import datetime

from app.models.enums import DocumentSourceType
from app.schemas.common import ORMModel


class ResumeVersionRead(ORMModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    version_number: int
    source_filename: str | None
    source_type: DocumentSourceType
    structured_data: dict | None
    parser_version: str | None
    created_at: datetime


class ResumeRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
