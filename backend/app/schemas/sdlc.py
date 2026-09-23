import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCharacteristics(BaseModel):
    requirements_volatility: int = Field(ge=1, le=5)
    compliance_criticality: int = Field(ge=1, le=5)
    technical_risk: int = Field(ge=1, le=5)
    customer_collaboration: int = Field(ge=1, le=5)
    release_frequency: int = Field(ge=1, le=5)
    team_experience: int = Field(ge=1, le=5)


class SDLCScore(BaseModel):
    scores: dict[str, float]
    recommendation: str
    rationale: str
    scoring_version: str = "1.0"


class SDLCRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    characteristics: dict[str, int]
    scores: dict[str, float]
    recommendation: str
    rationale: str
    scoring_version: str
    approval_status: str
    created_at: datetime
