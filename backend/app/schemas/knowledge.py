import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    filename: str
    content_type: str
    version: str
    jurisdiction: str
    effective_date: datetime | None
    status: str
    page_count: int
    created_at: datetime


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    limit: int = Field(default=5, ge=1, le=20)


class EvidenceChunk(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    content: str
    page_number: int | None
    section: str | None
    version: str
    jurisdiction: str
    effective_date: datetime | None
    score: float


class RetrievalResponse(BaseModel):
    items: list[EvidenceChunk]
