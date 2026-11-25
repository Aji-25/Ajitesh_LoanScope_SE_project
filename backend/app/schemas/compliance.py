import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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


class CompliancePassage(BaseModel):
    id: uuid.UUID
    filename: str
    section: str | None
    version: str
    content: str


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
    requirement_code: str = ""
    requirement_statement: str = ""
    needs_refresh: bool = False
    ai_reviewed: bool | None = None
    passages: list[CompliancePassage] = Field(default_factory=list)


class ComplianceRunResponse(BaseModel):
    items: list[ComplianceMappingResponse]
    evidence_available: bool


class ComplianceAgentInput(BaseModel):
    requirement: str
    evidence: list[EvidenceChunk]


class PolicyMatch(BaseModel):
    requirement_code: str
    decision: Literal["direct_match", "needs_review", "no_match"]
    passage: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=2, max_length=250)


class PolicyReview(BaseModel):
    matches: list[PolicyMatch]
