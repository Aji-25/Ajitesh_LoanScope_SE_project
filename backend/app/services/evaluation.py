import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    Approval,
    AuditEvent,
    ComplianceMapping,
    EvaluationRun,
    GeneratedArtifact,
    Project,
    Requirement,
    Risk,
)
from app.schemas.evaluation import AuditEvaluationResponse, AuditEventResponse, EvaluationResponse


@dataclass(frozen=True)
class EvaluationCounts:
    requirements: int
    complete_requirements: int
    compliance_mappings: int
    grounded_mappings: int
    risks: int
    approved: int
    artifacts: int


def calculate_metrics(counts: EvaluationCounts) -> dict[str, float]:
    requirements = max(1, counts.requirements)
    mappings = max(1, counts.compliance_mappings)
    return {
        "requirement_completeness": round(counts.complete_requirements / requirements * 100, 1),
        "evidence_grounding": round(counts.grounded_mappings / mappings * 100, 1),
        "risk_coverage": round(min(counts.risks / requirements, 1) * 100, 1),
        "approval_progress": round(min(counts.approved / requirements, 1) * 100, 1),
        "artifact_coverage": round(min(counts.artifacts / 9, 1) * 100, 1),
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
            await self.session.scalars(
                select(Requirement).where(Requirement.project_id == project_id)
            )
        )
        mappings = list(
            await self.session.scalars(
                select(ComplianceMapping).where(ComplianceMapping.project_id == project_id)
            )
        )
        risks = (
            await self.session.scalar(
                select(func.count(Risk.id)).where(Risk.project_id == project_id)
            )
            or 0
        )
        approved = (
            await self.session.scalar(
                select(func.count(Approval.id)).where(
                    Approval.project_id == project_id, Approval.status == "approved"
                )
            )
            or 0
        )
        artifacts = (
            await self.session.scalar(
                select(func.count(GeneratedArtifact.id)).where(
                    GeneratedArtifact.project_id == project_id
                )
            )
            or 0
        )
        counts = EvaluationCounts(
            len(requirements),
            sum(
                bool(item.acceptance_criteria) and not item.quality_findings
                for item in requirements
            ),
            len(mappings),
            sum(bool(item.evidence_chunk_ids) for item in mappings),
            risks,
            approved,
            artifacts,
        )
        metrics = calculate_metrics(counts)
        passed = metrics["requirement_completeness"] >= 80 and metrics["evidence_grounding"] >= 80
        record = EvaluationRun(
            project_id=project_id,
            metrics=metrics,
            passed=passed,
            summary="Quality gates passed."
            if passed
            else "Quality gaps remain; review metrics before approval.",
        )
        self.session.add(record)
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
                .where(AuditEvent.project_id == project_id)
                .order_by(AuditEvent.created_at.desc())
                .limit(100)
            )
        )
        evaluation = await self.session.scalar(
            select(EvaluationRun)
            .where(EvaluationRun.project_id == project_id)
            .order_by(EvaluationRun.created_at.desc())
            .limit(1)
        )
        return AuditEvaluationResponse(
            events=[AuditEventResponse.model_validate(item) for item in events],
            evaluation=EvaluationResponse.model_validate(evaluation) if evaluation else None,
        )
