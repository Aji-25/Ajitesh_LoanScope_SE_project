from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.db.session import database_is_ready
from app.schemas.health import HealthResponse, LivenessResponse

router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    return LivenessResponse(status="ok")


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": HealthResponse}},
)
async def readiness() -> HealthResponse | JSONResponse:
    if await database_is_ready():
        return HealthResponse(status="ok", database="connected")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=HealthResponse(status="unavailable", database="disconnected").model_dump(),
    )
