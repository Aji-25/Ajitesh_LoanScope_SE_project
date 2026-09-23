import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StakeholderInput(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    role: str = Field(min_length=2, max_length=120)
    organization: str | None = Field(default=None, max_length=160)

    @field_validator("name", "role", "organization", mode="before")
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    summary: str = Field(min_length=30, max_length=2000)
    product_type: str = Field(default="Digital personal loan origination", max_length=120)
    jurisdiction: str = Field(min_length=2, max_length=120)
    primary_stakeholder: StakeholderInput | None = None

    @field_validator("name", "summary", "product_type", "jurisdiction", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    summary: str
    product_type: str
    jurisdiction: str
    status: str
    current_stage: str
    created_at: datetime
    updated_at: datetime
    stakeholder_count: int = 0
    requirement_count: int = 0
    pending_approval_count: int = 0


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
