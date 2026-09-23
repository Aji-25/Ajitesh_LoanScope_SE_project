import uuid

from fastapi import APIRouter, HTTPException

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.approval import ApprovalDecision, ApprovalList, ApprovalResponse
from app.services.approvals import ApprovalService

router = APIRouter(prefix="/projects/{project_id}/approvals", tags=["approvals"])


@router.get("", response_model=ApprovalList)
async def list_approvals(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> ApprovalList:
    result = await ApprovalService(session).list(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/prepare", response_model=ApprovalList)
async def prepare_approvals(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> ApprovalList:
    result = await ApprovalService(session).prepare(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
async def decide_approval(
    project_id: uuid.UUID,
    approval_id: uuid.UUID,
    data: ApprovalDecision,
    user: CurrentUser,
    session: SessionDependency,
) -> ApprovalResponse:
    result = await ApprovalService(session).decide(project_id, approval_id, user.id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Approval not found.")
    return result
