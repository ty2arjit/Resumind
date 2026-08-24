"""Shared Pydantic base so every schema reads from ORM objects the same way."""

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
