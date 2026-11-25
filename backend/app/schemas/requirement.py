import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequirementCandidate(BaseModel):
    statement: str = Field(min_length=10)
    categories: list[str] = Field(min_length=1)
    source: str = Field(min_length=2)
    priority: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    clarification_needed: bool = False
    uncertainty_reason: str | None = None


class RequirementExtractionInput(BaseModel):
    project_id: uuid.UUID
    stakeholder_text: str = Field(min_length=10, max_length=5000)
    source_stakeholder: str = Field(min_length=2, max_length=160)
    accept_candidates: bool = True


class RequirementExtractionOutput(BaseModel):
    candidates: list[RequirementCandidate]
    summary: str


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    requirement_code: str
    statement: str
    categories: list[str]
    source_stakeholder: str
    priority: str | None
    assumptions: list[str]
    acceptance_criteria: list[str]
    confidence: float
    quality_findings: list[dict[str, str]]
    clarification_status: str
    version: int
    created_at: datetime


class RequirementQualityResponse(BaseModel):
    items: list[RequirementResponse]
    ambiguity_count: int
    conflict_count: int


class RequirementExtractionResponse(BaseModel):
    extraction: RequirementExtractionOutput
    persisted_requirements: list[RequirementResponse]


class RequirementListResponse(BaseModel):
    items: list[RequirementResponse]
    total: int


class RequirementClarificationInput(BaseModel):
    statement: str = Field(min_length=10, max_length=5000)
    acceptance_criteria: list[str] | None = Field(default=None, max_length=20)
    reason: str = Field(default="Requirement edited", min_length=3, max_length=255)

    @field_validator("statement", mode="before")
    @classmethod
    def strip_statement(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("acceptance_criteria")
    @classmethod
    def strip_criteria(cls, values: list[str] | None) -> list[str] | None:
        return [value.strip() for value in values if value.strip()] if values is not None else None
