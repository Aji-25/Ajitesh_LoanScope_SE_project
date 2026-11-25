import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    AuditEvent,
    ComplianceMapping,
    EvaluationRun,
    GeneratedArtifact,
    Project,
    Requirement,
    RequirementVersion,
)
from app.schemas.evaluation import (
    AuditEvaluationResponse,
    AuditEventResponse,
    EvaluationResponse,
    EvaluationReview,
)
from app.services.llm import get_live_llm_service
from app.services.requirement_quality import review_requirements


@dataclass(frozen=True)
class EvaluationCounts:
    requirements: int
    clear_requirements: int
    grounded_requirements: int
    risk_reviewed_requirements: int
    artifact_types: int


DOCUMENT_TYPES = 9


def calculate_metrics(counts: EvaluationCounts) -> dict[str, float]:
    total = max(1, counts.requirements)
    return {
        "requirement_completeness": round(counts.clear_requirements / total * 100, 1),
        "evidence_grounding": round(counts.grounded_requirements / total * 100, 1),
        "risk_coverage": round(counts.risk_reviewed_requirements / total * 100, 1),
        "artifact_coverage": round(counts.artifact_types / DOCUMENT_TYPES * 100, 1),
    }


class EvaluationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _owns(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> bool:
        return (
            await self.session.scalar(
                select(Project.id).where(
                    Project.id == project_id, Project.created_by_id == owner_id
                )
            )
            is not None
        )

    async def run(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> EvaluationResponse | None:
        if not await self._owns(project_id, owner_id):
            return None
        requirements = list(
            await self.session.scalars(select(Requirement).where(Requirement.active_in(project_id)))
        )
        requirement_changed = (
            select(RequirementVersion.id)
            .where(
                RequirementVersion.requirement_id == ComplianceMapping.requirement_id,
                RequirementVersion.created_at > ComplianceMapping.created_at,
            )
            .exists()
        )
        grounded = await self.session.scalar(
            select(func.count(func.distinct(ComplianceMapping.requirement_id))).where(
                ComplianceMapping.project_id == project_id,
                ComplianceMapping.requirement_id.in_(Requirement.active_ids(project_id)),
                ComplianceMapping.ai_reviewed.is_(True),
                func.jsonb_array_length(ComplianceMapping.evidence_chunk_ids) > 0,
                ~requirement_changed,
            )
        )
        review = await self.session.scalar(
            select(AuditEvent)
            .where(AuditEvent.project_id == project_id, AuditEvent.entity_type == "security_review")
            .order_by(AuditEvent.created_at.desc())
            .limit(1)
        )
        reviewed_versions = review.event_metadata.get("requirement_versions", {}) if review else {}
        artifacts = await self.session.scalar(
            select(func.count(func.distinct(GeneratedArtifact.artifact_type))).where(
                GeneratedArtifact.project_id == project_id
            )
        )
        counts = EvaluationCounts(
            requirements=len(requirements),
            clear_requirements=sum(not findings for findings in review_requirements(requirements)),
            grounded_requirements=grounded or 0,
            risk_reviewed_requirements=sum(
                reviewed_versions.get(str(item.id)) == item.version for item in requirements
            ),
            artifact_types=artifacts or 0,
        )
        metrics = calculate_metrics(counts)
        await self.session.commit()

        ai_review = await get_live_llm_service().structured_generate(
            system_prompt=(
                "Explain this project snapshot in at most two short sentences. Give up to three "
                "short next steps grounded in the counts. Clear requirements have no flagged "
                "wording issues. Evidence grounding means a current requirement has a matched "
                "policy passage. Risk coverage counts requirement versions reviewed, including "
                "reviews that found no risk. Document coverage counts types generated. "
                "Never infer legal compliance, test results or project facts beyond these counts."
            ),
            user_input={
                "active_requirements": counts.requirements,
                "clear_requirements": counts.clear_requirements,
                "requirements_with_policy_evidence": counts.grounded_requirements,
                "requirements_reviewed_for_risk": counts.risk_reviewed_requirements,
                "document_types_generated": counts.artifact_types,
                "document_types_available": DOCUMENT_TYPES,
            },
            response_model=EvaluationReview,
        )
        if not await self._owns(project_id, owner_id):
            return None
        record = EvaluationRun(
            project_id=project_id,
            metrics=metrics,
            passed=metrics["requirement_completeness"] >= 80
            and metrics["evidence_grounding"] >= 80,
            summary=ai_review.summary,
            review_actions=ai_review.next_steps,
        )
        self.session.add(record)
        await self.session.flush()
        self.session.add(
            AuditEvent(
                project_id=project_id,
                actor_type="agent",
                agent_name="live_ai",
                action="Reviewed the project snapshot with AI",
                entity_type="evaluation_run",
                entity_id=record.id,
                event_metadata={"metrics": metrics},
            )
        )
        await self.session.commit()
        return EvaluationResponse.model_validate(record)

    async def dashboard(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> AuditEvaluationResponse | None:
        if not await self._owns(project_id, owner_id):
            return None
        events = list(
            await self.session.scalars(
                select(AuditEvent)
                .where(AuditEvent.project_id == project_id, AuditEvent.entity_type != "approval")
                .order_by(AuditEvent.created_at.desc())
                .limit(100)
            )
        )
        evaluation = await self.session.scalar(
            select(EvaluationRun)
            .where(
                EvaluationRun.project_id == project_id, EvaluationRun.review_actions.is_not(None)
            )
            .order_by(EvaluationRun.created_at.desc())
            .limit(1)
        )
        return AuditEvaluationResponse(
            events=[AuditEventResponse.model_validate(item) for item in events],
            evaluation=EvaluationResponse.model_validate(evaluation) if evaluation else None,
        )
