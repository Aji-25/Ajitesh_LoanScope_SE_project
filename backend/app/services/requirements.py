import uuid
from datetime import UTC, datetime

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.requirement import RequirementAgent
from app.core.config import get_settings
from app.db.repositories.audit import AuditRepository
from app.models.database import (
    AuditEvent,
    Conversation,
    Message,
    Project,
    Requirement,
    RequirementVersion,
)
from app.schemas.requirement import (
    RequirementClarificationInput,
    RequirementExtractionInput,
    RequirementExtractionResponse,
    RequirementListResponse,
    RequirementQualityResponse,
    RequirementResponse,
)
from app.services.llm import get_live_llm_service
from app.services.requirement_quality import apply_quality_checks


class RequirementService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _owns_project(
        self, project_id: uuid.UUID, owner_id: uuid.UUID, *, lock: bool = False
    ) -> bool:
        query = select(Project.id).where(
            Project.id == project_id, Project.created_by_id == owner_id
        )
        return await self.session.scalar(query.with_for_update() if lock else query) is not None

    async def _load_requirements(self, project_id: uuid.UUID) -> list[Requirement]:
        return list(
            await self.session.scalars(
                select(Requirement)
                .where(Requirement.active_in(project_id))
                .order_by(Requirement.requirement_code)
            )
        )

    async def extract(
        self,
        project_id: uuid.UUID,
        owner_id: uuid.UUID,
        data: RequirementExtractionInput,
    ) -> RequirementExtractionResponse | None:
        if not await self._owns_project(project_id, owner_id):
            return None

        # The provider can take several seconds. Lock the project only when saving its results.
        await self.session.commit()
        result = await RequirementAgent(get_live_llm_service()).run(data)
        if not await self._owns_project(project_id, owner_id, lock=True):
            return None

        conversation = await self.session.scalar(
            select(Conversation).where(Conversation.project_id == project_id).limit(1)
        )
        if conversation is None:
            conversation = Conversation(
                project_id=project_id,
                title="Stakeholder discovery",
                status="in_progress",
            )
            self.session.add(conversation)
            await self.session.flush()

        self.session.add(
            Message(
                conversation_id=conversation.id,
                role="stakeholder",
                content=data.stakeholder_text,
                source_name=data.source_stakeholder,
                extraction_metadata=result.model_dump(mode="json"),
            )
        )
        last_number = await self.session.scalar(
            select(func.max(cast(func.substr(Requirement.requirement_code, 5), Integer))).where(
                Requirement.project_id == project_id
            )
        )
        requirements = await self._load_requirements(project_id)
        saved = [
            Requirement(
                project_id=project_id,
                requirement_code=f"REQ-{index:03d}",
                statement=item.statement,
                categories=item.categories,
                source_stakeholder=data.source_stakeholder,
                priority=item.priority,
                assumptions=item.assumptions,
                acceptance_criteria=item.acceptance_criteria,
                confidence=item.confidence,
            )
            for index, item in enumerate(result.candidates, start=(last_number or 0) + 1)
        ]
        self.session.add_all(saved)
        apply_quality_checks(requirements + saved)

        conversation.status = "in_progress"
        AuditRepository(self.session).add(
            AuditEvent(
                project_id=project_id,
                actor_type="agent",
                agent_name="requirement_agent",
                action="Extracted structured requirements",
                entity_type="conversation",
                entity_id=conversation.id,
                event_metadata={
                    "provider_mode": get_settings().llm_mode,
                    "requirement_count": len(saved),
                    "uncertainty_count": sum(
                        item.clarification_needed for item in result.candidates
                    ),
                },
            )
        )
        await self.session.commit()
        return RequirementExtractionResponse(
            extraction=result,
            persisted_requirements=[RequirementResponse.model_validate(item) for item in saved],
        )

    async def list_requirements(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> RequirementListResponse | None:
        if not await self._owns_project(project_id, owner_id):
            return None
        requirements = await self._load_requirements(project_id)
        apply_quality_checks(requirements)
        return RequirementListResponse(
            items=[RequirementResponse.model_validate(item) for item in requirements],
            total=len(requirements),
        )

    async def analyze_quality(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> RequirementQualityResponse | None:
        if not await self._owns_project(project_id, owner_id, lock=True):
            return None
        requirements = await self._load_requirements(project_id)
        apply_quality_checks(requirements)
        await self.session.commit()
        findings = [finding for item in requirements for finding in item.quality_findings]
        return RequirementQualityResponse(
            items=[RequirementResponse.model_validate(item) for item in requirements],
            ambiguity_count=sum(finding["kind"] == "ambiguity" for finding in findings),
            conflict_count=sum(finding["kind"] == "conflict" for finding in findings),
        )

    async def clarify(
        self,
        project_id: uuid.UUID,
        requirement_id: uuid.UUID,
        owner_id: uuid.UUID,
        data: RequirementClarificationInput,
    ) -> RequirementResponse | None:
        if not await self._owns_project(project_id, owner_id, lock=True):
            return None
        requirements = await self._load_requirements(project_id)
        requirement = next((item for item in requirements if item.id == requirement_id), None)
        if requirement is None:
            return None

        criteria = (
            requirement.acceptance_criteria
            if data.acceptance_criteria is None
            else data.acceptance_criteria
        )
        if requirement.statement != data.statement or requirement.acceptance_criteria != criteria:
            self.session.add(
                RequirementVersion(
                    requirement_id=requirement.id,
                    version=requirement.version,
                    statement=requirement.statement,
                    acceptance_criteria=requirement.acceptance_criteria,
                    quality_findings=requirement.quality_findings,
                    changed_by_id=owner_id,
                    change_reason=data.reason,
                )
            )
            requirement.statement = data.statement
            requirement.acceptance_criteria = criteria
            requirement.version += 1
            AuditRepository(self.session).add(
                AuditEvent(
                    project_id=project_id,
                    actor_type="user",
                    actor_id=owner_id,
                    action="Edited requirement",
                    entity_type="requirement",
                    entity_id=requirement.id,
                    event_metadata={"version": requirement.version, "reason": data.reason},
                )
            )
        apply_quality_checks(requirements)
        await self.session.commit()
        return RequirementResponse.model_validate(requirement)

    async def delete(
        self, project_id: uuid.UUID, requirement_id: uuid.UUID, owner_id: uuid.UUID
    ) -> RequirementListResponse | None:
        if not await self._owns_project(project_id, owner_id, lock=True):
            return None
        requirements = await self._load_requirements(project_id)
        requirement = next((item for item in requirements if item.id == requirement_id), None)
        if requirement is None:
            return None

        requirement.deleted_at = datetime.now(UTC)
        requirements.remove(requirement)
        apply_quality_checks(requirements)
        AuditRepository(self.session).add(
            AuditEvent(
                project_id=project_id,
                actor_type="user",
                actor_id=owner_id,
                action=f"Deleted requirement {requirement.requirement_code}",
                entity_type="requirement",
                entity_id=requirement.id,
                event_metadata={
                    "requirement_code": requirement.requirement_code,
                    "version": requirement.version,
                },
            )
        )
        await self.session.commit()
        return RequirementListResponse(
            items=[RequirementResponse.model_validate(item) for item in requirements],
            total=len(requirements),
        )
