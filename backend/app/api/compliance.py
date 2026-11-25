import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.compliance import ComplianceRunResponse
from app.services.compliance import ComplianceService
from app.services.llm import LLMServiceError

router = APIRouter(prefix="/projects/{project_id}/compliance", tags=["compliance"])


@router.get("", response_model=ComplianceRunResponse)
async def list_compliance(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> ComplianceRunResponse:
    result = await ComplianceService(session).list(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/analyze", response_model=ComplianceRunResponse)
async def analyze_compliance(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> ComplianceRunResponse:
    try:
        result = await ComplianceService(session).analyze(project_id, user.id)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result
