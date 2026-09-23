import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.compliance import ComplianceRunResponse
from app.services.compliance import ComplianceService

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
    result = await ComplianceService(session).analyze(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result
