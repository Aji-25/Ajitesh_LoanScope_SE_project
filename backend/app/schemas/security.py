import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def review_headline(title: str) -> str:
    missing = re.fullmatch(r"(?:missing|lack of|no)\s+(.+)", title.strip(), re.I)
    if missing:
        subject = missing[1]
    else:
        failed = re.fullmatch(
            r"(.+?)\s+(?:(?:is|are|was|were)\s+)?not\s+"
            r"(?:enforced|implemented|validated|verified|recorded)(\b.*)",
            title.strip(),
            re.I,
        )
        if not failed:
            return title
        subject = f"{failed[1]}{failed[2]}"
    if len(subject) < 2 or not subject[1].isupper():
        subject = subject[0].lower() + subject[1:]
    return f"Verify {subject}"


class RiskAssessment(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    remaining_risk: str = Field(min_length=3, max_length=320)
    next_step: str = Field(min_length=3, max_length=320)
    likelihood_reason: str = Field(min_length=3, max_length=200)
    impact_reason: str = Field(min_length=3, max_length=200)
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)

    _review_headline = field_validator("title")(review_headline)


class RiskReview(BaseModel):
    risk: RiskAssessment | None


class RiskScreen(BaseModel):
    keep: list[int]


class SecurityFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    requirement_id: uuid.UUID
    category: str
    title: str
    description: str
    severity: str
    recommendation: str
    status: str
    created_at: datetime

    _review_headline = field_validator("title")(review_headline)


class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    requirement_id: uuid.UUID | None
    risk_code: str
    category: str
    description: str
    likelihood: int
    impact: int
    score: int
    mitigation: str
    existing_control: str | None
    rating_reason: str | None
    owner_role: str
    status: str
    created_at: datetime


class SecurityRiskResponse(BaseModel):
    findings: list[SecurityFindingResponse]
    risks: list[RiskResponse]
