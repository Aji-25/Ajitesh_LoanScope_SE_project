import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.evaluation import AuditEvaluationResponse, EvaluationResponse
from app.services.evaluation import EvaluationService
from app.services.llm import LLMServiceError

router = APIRouter(prefix="/projects/{project_id}", tags=["audit", "evaluation"])


@router.get("/audit", response_model=AuditEvaluationResponse)
async def audit_dashboard(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> AuditEvaluationResponse:
    result = await EvaluationService(session).dashboard(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/evaluations", response_model=EvaluationResponse)
async def run_evaluation(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> EvaluationResponse:
    try:
        result = await EvaluationService(session).run(project_id, user.id)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result
