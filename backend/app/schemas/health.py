from typing import Literal

from pydantic import BaseModel


class LivenessResponse(BaseModel):
    status: Literal["ok"]


class HealthResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    database: Literal["connected", "disconnected"]
