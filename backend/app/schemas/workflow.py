import uuid
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStart(BaseModel):
    max_iterations: int = Field(default=2, ge=1, le=5)


class WorkflowResume(BaseModel):
    clarifications: list[str] = Field(min_length=1, max_length=500)


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    thread_id: str
    status: str
    current_node: str
    state: dict[str, Any]
