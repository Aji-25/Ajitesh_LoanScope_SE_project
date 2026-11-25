import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.knowledge import EvidenceChunk


class ComplianceAssessment(BaseModel):
    obligation: str
    applicability: str
    rationale: str
    evidence_chunk_ids: list[uuid.UUID]
    citations: list[dict[str, str | int | None]]
    confidence: float
    gap_status: str
    human_review_required: bool


class ComplianceMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    requirement_id: uuid.UUID
    obligation: str
    applicability: str
    rationale: str
    evidence_chunk_ids: list[str]
    citations: list[dict[str, str | int | None]]
    confidence: float
    status: str
    gap_status: str
    human_review_required: bool
    created_at: datetime


class ComplianceRunResponse(BaseModel):
    items: list[ComplianceMappingResponse]
    evidence_available: bool


class ComplianceAgentInput(BaseModel):
    requirement: str
    evidence: list[EvidenceChunk]
