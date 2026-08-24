import uuid
from datetime import datetime

from app.models.enums import DocumentSourceType
from app.schemas.common import ORMModel


class JobDescriptionRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    company: str | None
    source_type: DocumentSourceType
    structured_data: dict | None
    created_at: datetime
