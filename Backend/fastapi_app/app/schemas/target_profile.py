import uuid
from datetime import datetime

from app.schemas.common import ORMModel


class TargetProfileRead(ORMModel):
    id: uuid.UUID
    is_system: bool
    position: str
    domain: str | None
    profile_version: str
    profile_data: dict | None
    created_at: datetime
