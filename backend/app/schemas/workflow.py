import uuid
from typing import Any

from pydantic import BaseModel


class WorkflowStart(BaseModel):
    max_iterations: int = 2


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    thread_id: str
    status: str
    current_node: str
    state: dict[str, Any]
