import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectCharacteristics(BaseModel):
    requirements_volatility: int = Field(ge=1, le=5)
    compliance_criticality: int = Field(ge=1, le=5)
    technical_risk: int = Field(ge=1, le=5)
    customer_collaboration: int = Field(ge=1, le=5)
    release_frequency: int = Field(ge=1, le=5)
    team_experience: int = Field(ge=1, le=5)


class SDLCSuggestion(BaseModel):
    requirements_volatility: int | None = Field(default=None, ge=1, le=5)
    compliance_criticality: int | None = Field(default=None, ge=1, le=5)
    technical_risk: int | None = Field(default=None, ge=1, le=5)
    customer_collaboration: int | None = Field(default=None, ge=1, le=5)
    release_frequency: int | None = Field(default=None, ge=1, le=5)
    team_experience: int | None = Field(default=None, ge=1, le=5)
    rationale: str = Field(min_length=1, max_length=1000)
    assumptions: list[
        Literal[
            "requirements_volatility", "compliance_criticality", "technical_risk",
            "customer_collaboration", "release_frequency", "team_experience",
        ]
    ] = Field(default_factory=list, max_length=6)


class LiveSDLCInputs(SDLCSuggestion):
    requirements_volatility: int = Field(ge=1, le=5)
    compliance_criticality: int = Field(ge=1, le=5)
    technical_risk: int = Field(ge=1, le=5)
    customer_collaboration: int = Field(ge=1, le=5)
    release_frequency: int = Field(ge=1, le=5)
    team_experience: int = Field(ge=1, le=5)
    rationale: str = Field(min_length=1, max_length=240)


class SDLCScore(BaseModel):
    scores: dict[str, float]
    recommendation: str
    rationale: str
    scoring_version: str = "1.0"


class SDLCSuggestionResponse(SDLCSuggestion):
    characteristics: ProjectCharacteristics
    preview: SDLCScore


class SDLCRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    characteristics: dict[str, int]
    scores: dict[str, float]
    recommendation: str
    rationale: str
    scoring_version: str
    created_at: datetime
