import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    actor_type: str
    actor_id: uuid.UUID | None
    agent_name: str | None
    action: str
    entity_type: str
    entity_id: uuid.UUID | None
    event_metadata: dict[str, Any]
    created_at: datetime


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    metrics: dict[str, float]
    passed: bool
    summary: str
    created_at: datetime


class AuditEvaluationResponse(BaseModel):
    events: list[AuditEventResponse]
    evaluation: EvaluationResponse | None
