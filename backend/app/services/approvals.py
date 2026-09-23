import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Approval, AuditEvent, Project, Requirement
from app.schemas.approval import ApprovalDecision, ApprovalList, ApprovalResponse


class ApprovalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def prepare(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> ApprovalList | None:
        project = await self.session.scalar(
            select(Project).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        existing = list(
            await self.session.scalars(select(Approval).where(Approval.project_id == project_id))
        )
        if not existing:
            count = len(
                list(
                    await self.session.scalars(
                        select(Requirement.id).where(Requirement.project_id == project_id)
                    )
                )
            )
            approval = Approval(
                project_id=project_id,
                entity_type="requirement_baseline",
                title=f"Approve {count} requirement baseline",
                assigned_role="Business Analyst",
                workflow_thread_id=f"approval-{uuid.uuid4()}",
                request_payload={"requirement_count": count, "project_name": project.name},
            )
            self.session.add(approval)
            await self.session.commit()
            existing = [approval]
        return ApprovalList(items=[ApprovalResponse.model_validate(item) for item in existing])

    async def list(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> ApprovalList | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        items = list(
            await self.session.scalars(
                select(Approval)
                .where(Approval.project_id == project_id)
                .order_by(Approval.created_at.desc())
            )
        )
        return ApprovalList(items=[ApprovalResponse.model_validate(item) for item in items])

    async def decide(
        self,
        project_id: uuid.UUID,
        approval_id: uuid.UUID,
        user_id: uuid.UUID,
        data: ApprovalDecision,
    ) -> ApprovalResponse | None:
        approval = await self.session.scalar(
            select(Approval)
            .join(Project)
            .where(
                Approval.id == approval_id,
                Approval.project_id == project_id,
                Project.created_by_id == user_id,
            )
        )
        if approval is None:
            return None
        status = {
            "approve": "approved",
            "reject": "rejected",
            "edit": "revision_requested",
            "regenerate": "revision_requested",
        }[data.action]
        approval.status = status
        approval.decision_comment = data.comment
        approval.decided_by_id = user_id
        approval.decided_at = datetime.now(UTC)
        approval.decision_payload = {"action": data.action, "edits": data.edits}
        self.session.add(
            AuditEvent(
                project_id=project_id,
                actor_type="human",
                actor_id=user_id,
                action=f"Approval {data.action}",
                entity_type="approval",
                entity_id=approval.id,
                event_metadata={"status": status, "comment": data.comment},
            )
        )
        await self.session.commit()
        return ApprovalResponse.model_validate(approval)
