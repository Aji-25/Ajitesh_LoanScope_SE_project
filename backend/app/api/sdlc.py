import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.sdlc import (
    ProjectCharacteristics,
    SDLCRecommendationResponse,
    SDLCSuggestionResponse,
)
from app.services.llm import LLMServiceError
from app.services.sdlc import SDLCService

router = APIRouter(prefix="/projects/{project_id}/sdlc", tags=["sdlc"])


@router.post("/suggest", response_model=SDLCSuggestionResponse)
async def suggest_sdlc(
    project_id: uuid.UUID,
    user: CurrentUser,
    session: SessionDependency,
    data: ProjectCharacteristics | None = None,
) -> SDLCSuggestionResponse:
    try:
        result = await SDLCService(session).suggest(project_id, user.id, data)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


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
