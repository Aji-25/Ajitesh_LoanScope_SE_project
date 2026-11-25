import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.security import SecurityRiskResponse
from app.services.llm import LLMServiceError
from app.services.security import SecurityRiskService

router = APIRouter(prefix="/projects/{project_id}/security-risk", tags=["security", "risk"])


@router.get("", response_model=SecurityRiskResponse)
async def list_security_risks(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> SecurityRiskResponse:
    result = await SecurityRiskService(session).list(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/generate", response_model=SecurityRiskResponse)
async def generate_security_risks(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> SecurityRiskResponse:
    try:
        result = await SecurityRiskService(session).generate(project_id, user.id)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result
