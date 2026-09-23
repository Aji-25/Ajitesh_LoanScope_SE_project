import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.requirement import (
    RequirementExtractionInput,
    RequirementExtractionResponse,
    RequirementListResponse,
    RequirementQualityResponse,
)
from app.services.llm import LLMServiceError
from app.services.requirements import RequirementService

router = APIRouter(prefix="/projects/{project_id}", tags=["requirements"])


@router.post(
    "/messages", response_model=RequirementExtractionResponse, status_code=status.HTTP_201_CREATED
)
async def capture_message(
    project_id: uuid.UUID,
    data: RequirementExtractionInput,
    user: CurrentUser,
    session: SessionDependency,
) -> RequirementExtractionResponse:
    try:
        result = await RequirementService(session).extract(project_id, user.id, data)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/requirements/analyze", response_model=RequirementQualityResponse)
async def analyze_requirements(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> RequirementQualityResponse:
    result = await RequirementService(session).analyze_quality(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.get("/requirements", response_model=RequirementListResponse)
async def list_requirements(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> RequirementListResponse:
    result = await RequirementService(session).list_requirements(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result
