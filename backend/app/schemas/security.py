import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
    owner_role: str
    status: str
    created_at: datetime


class SecurityRiskResponse(BaseModel):
    findings: list[SecurityFindingResponse]
    risks: list[RiskResponse]
