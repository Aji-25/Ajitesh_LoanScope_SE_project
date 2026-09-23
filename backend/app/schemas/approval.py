import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID | None
    title: str
    assigned_role: str
    status: str
    decision_comment: str | None
    workflow_thread_id: str | None
    request_payload: dict[str, Any]
    decision_payload: dict[str, Any]
    created_at: datetime
    decided_at: datetime | None


class ApprovalDecision(BaseModel):
    action: Literal["approve", "reject", "edit", "regenerate"]
    comment: str = Field(min_length=2, max_length=1000)
    edits: dict[str, Any] = Field(default_factory=dict)


class ApprovalList(BaseModel):
    items: list[ApprovalResponse]
