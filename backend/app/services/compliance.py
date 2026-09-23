import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.compliance import ComplianceAgent
from app.models.database import ComplianceMapping, Project, Requirement
from app.schemas.compliance import (
    ComplianceAgentInput,
    ComplianceMappingResponse,
    ComplianceRunResponse,
)
from app.services.knowledge import KnowledgeService


class ComplianceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def analyze(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> ComplianceRunResponse | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        requirements = list(
            await self.session.scalars(
                select(Requirement).where(Requirement.project_id == project_id)
            )
        )
        await self.session.execute(
            delete(ComplianceMapping).where(ComplianceMapping.project_id == project_id)
        )
        mappings: list[ComplianceMapping] = []
        agent = ComplianceAgent()
        for requirement in requirements:
            retrieval = await KnowledgeService(self.session).retrieve(
                project_id, owner_id, requirement.statement, 3
            )
            assessment = agent.run(
                ComplianceAgentInput(
                    requirement=requirement.statement, evidence=retrieval.items if retrieval else []
                )
            )
            mapping = ComplianceMapping(
                project_id=project_id,
                requirement_id=requirement.id,
                obligation=assessment.obligation,
                applicability=assessment.applicability,
                rationale=assessment.rationale,
                evidence_chunk_ids=[str(item) for item in assessment.evidence_chunk_ids],
                citations=assessment.citations,
                confidence=assessment.confidence,
            )
            self.session.add(mapping)
            mappings.append(mapping)
        await self.session.commit()
        return ComplianceRunResponse(
            items=[ComplianceMappingResponse.model_validate(item) for item in mappings],
            evidence_available=any(item.evidence_chunk_ids for item in mappings),
        )

    async def list(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> ComplianceRunResponse | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        items = list(
            await self.session.scalars(
                select(ComplianceMapping)
                .where(ComplianceMapping.project_id == project_id)
                .order_by(ComplianceMapping.created_at)
            )
        )
        return ComplianceRunResponse(
            items=[ComplianceMappingResponse.model_validate(item) for item in items],
            evidence_available=any(item.evidence_chunk_ids for item in items),
        )
