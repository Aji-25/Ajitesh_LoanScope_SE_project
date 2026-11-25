import uuid
from datetime import UTC, datetime

from langgraph.types import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Approval, AuditEvent, Project, Requirement, SDLCRecommendation
from app.schemas.approval import ApprovalDecision, ApprovalList, ApprovalResponse
from app.services.sdlc import MODEL_LABELS, SCORING_VERSION
from app.workflows.approval import ApprovalState, build_approval_graph
from app.workflows.checkpoints import postgres_checkpointer

MAX_REGENERATIONS = 3


class ApprovalConflictError(ValueError):
    pass


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
        created: list[Approval] = []
        if not any(item.entity_type == "requirement_baseline" for item in existing):
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
            created.append(approval)
        sdlc = await self.session.scalar(
            select(SDLCRecommendation)
            .where(
                SDLCRecommendation.project_id == project_id,
                SDLCRecommendation.scoring_version == SCORING_VERSION,
            )
            .order_by(SDLCRecommendation.created_at.desc())
            .limit(1)
        )
        if sdlc and not any(
            item.entity_type == "sdlc_recommendation" and item.entity_id == sdlc.id
            for item in existing
        ):
            model_label = MODEL_LABELS.get(sdlc.recommendation, sdlc.recommendation)
            approval = Approval(
                project_id=project_id,
                entity_type="sdlc_recommendation",
                entity_id=sdlc.id,
                title=f"Approve {model_label} recommendation",
                assigned_role="Project Manager",
                workflow_thread_id=f"approval-{uuid.uuid4()}",
                request_payload={"recommendation": sdlc.recommendation, "scores": sdlc.scores},
            )
            self.session.add(approval)
            created.append(approval)
        if created:
            await self.session.commit()
            async with postgres_checkpointer() as saver:
                graph = build_approval_graph(saver)
                for approval in created:
                    await graph.ainvoke(
                        ApprovalState(
                            approval_id=str(approval.id),
                            title=approval.title,
                            payload=approval.request_payload,
                            decision=None,
                            decision_payload={},
                            status="pending",
                        ),
                        {"configurable": {"thread_id": approval.workflow_thread_id}},
                    )
            existing.extend(created)
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
        if approval.status != "pending":
            raise ApprovalConflictError("This approval has already been decided.")
        regeneration_count = int(approval.request_payload.get("regeneration_count", 0))
        if data.action == "regenerate" and regeneration_count >= MAX_REGENERATIONS:
            raise ApprovalConflictError("The regeneration limit has been reached.")
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
        if approval.workflow_thread_id:
            async with postgres_checkpointer() as saver:
                graph = build_approval_graph(saver)
                await graph.ainvoke(
                    Command(
                        resume={
                            "action": data.action,
                            "comment": data.comment,
                            "edits": data.edits,
                        }
                    ),
                    {"configurable": {"thread_id": approval.workflow_thread_id}},
                )
        if data.action == "edit":
            approval.request_payload = {
                **approval.request_payload,
                "human_edits": data.edits,
            }
        if data.action == "regenerate":
            approval.status = "pending"
            approval.workflow_thread_id = f"approval-{uuid.uuid4()}"
            approval.request_payload = {
                **approval.request_payload,
                "regeneration_count": regeneration_count + 1,
                "last_regeneration_comment": data.comment,
            }
            approval.decision_comment = None
            approval.decided_by_id = None
            approval.decided_at = None
            async with postgres_checkpointer() as saver:
                graph = build_approval_graph(saver)
                await graph.ainvoke(
                    ApprovalState(
                        approval_id=str(approval.id),
                        title=approval.title,
                        payload=approval.request_payload,
                        decision=None,
                        decision_payload={},
                        status="pending",
                    ),
                    {"configurable": {"thread_id": approval.workflow_thread_id}},
                )
        await self.session.commit()
        return ApprovalResponse.model_validate(approval)
