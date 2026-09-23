import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    artifact_type: str
    title: str
    version: int
    content: dict[str, Any]
    source_requirement_ids: list[str]
    created_at: datetime


class ArtifactList(BaseModel):
    items: list[ArtifactResponse]
