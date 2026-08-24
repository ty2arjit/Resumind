import uuid
from datetime import datetime

from app.schemas.common import ORMModel


class UserRead(ORMModel):
    id: uuid.UUID
    email: str
    name: str
    college: str | None
    created_at: datetime
