import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.workflow import WorkflowResponse, WorkflowResume, WorkflowStart
from app.services.workflows import WorkflowService

router = APIRouter(tags=["workflows"])


@router.post(
    "/projects/{project_id}/workflows",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_workflow(
    project_id: uuid.UUID, data: WorkflowStart, user: CurrentUser, session: SessionDependency
) -> WorkflowResponse:
    result = await WorkflowService(session).start(project_id, user.id, data.max_iterations)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.get("/workflows/{run_id}", response_model=WorkflowResponse)
async def get_workflow(
    run_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> WorkflowResponse:
    result = await WorkflowService(session).get(run_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return result


@router.get(
    "/projects/{project_id}/workflows/latest",
    response_model=WorkflowResponse | None,
)
async def latest_workflow(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> WorkflowResponse | None:
    return await WorkflowService(session).latest(project_id, user.id)


@router.post("/workflows/{run_id}/resume", response_model=WorkflowResponse)
async def resume_workflow(
    run_id: uuid.UUID,
    data: WorkflowResume,
    user: CurrentUser,
    session: SessionDependency,
) -> WorkflowResponse:
    try:
        result = await WorkflowService(session).resume(run_id, user.id, data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return result
