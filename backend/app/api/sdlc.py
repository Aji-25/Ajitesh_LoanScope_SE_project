import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.sdlc import ProjectCharacteristics, SDLCRecommendationResponse
from app.services.sdlc import SDLCService

router = APIRouter(prefix="/projects/{project_id}/sdlc", tags=["sdlc"])


@router.post("/recommend", response_model=SDLCRecommendationResponse)
async def recommend_sdlc(
    project_id: uuid.UUID,
    data: ProjectCharacteristics,
    user: CurrentUser,
    session: SessionDependency,
) -> SDLCRecommendationResponse:
    result = await SDLCService(session).calculate(project_id, user.id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.get("/latest", response_model=SDLCRecommendationResponse)
async def latest_sdlc(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> SDLCRecommendationResponse:
    result = await SDLCService(session).latest(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="No recommendation found.")
    return result
