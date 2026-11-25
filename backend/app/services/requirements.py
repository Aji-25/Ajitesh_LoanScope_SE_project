import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.requirement import RequirementAgent
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
from app.services.llm import get_llm_service
from app.services.requirement_quality import analyze_statement, detect_conflicts


class RequirementService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def extract(
        self,
        project_id: uuid.UUID,
        owner_id: uuid.UUID,
        data: RequirementExtractionInput,
    ) -> RequirementExtractionResponse | None:
        project = await self.session.scalar(
            select(Project).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
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

        result = await RequirementAgent(get_llm_service()).run(data)
        message = Message(
            conversation_id=conversation.id,
            role="stakeholder",
            content=data.stakeholder_text,
            source_name=data.source_stakeholder,
            extraction_metadata=result.model_dump(mode="json"),
        )
        self.session.add(message)

        existing_count = await self.session.scalar(
            select(func.count(Requirement.id)).where(Requirement.project_id == project_id)
        )
        saved: list[Requirement] = []
        for index, item in enumerate(result.candidates, start=(existing_count or 0) + 1):
            findings = analyze_statement(item.statement, item.acceptance_criteria)
            requirement = Requirement(
                project_id=project_id,
                requirement_code=f"REQ-{index:03d}",
                statement=item.statement,
                categories=item.categories,
                source_stakeholder=data.source_stakeholder,
                priority=item.priority,
                assumptions=item.assumptions,
                acceptance_criteria=item.acceptance_criteria,
                confidence=item.confidence,
                quality_findings=[finding.as_dict() for finding in findings],
                clarification_status="required" if findings else "not_required",
            )
            self.session.add(requirement)
            saved.append(requirement)

        conversation.status = "in_progress"
        await self.session.flush()
        AuditRepository(self.session).add(
            AuditEvent(
                project_id=project_id,
                actor_type="agent",
                agent_name="requirement_agent",
                action="Extracted structured requirements",
                entity_type="conversation",
                entity_id=conversation.id,
                event_metadata={
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
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        items = list(
            await self.session.scalars(
                select(Requirement)
                .where(Requirement.project_id == project_id)
                .order_by(Requirement.requirement_code)
            )
        )
        return RequirementListResponse(
            items=[RequirementResponse.model_validate(item) for item in items], total=len(items)
        )

    async def analyze_quality(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> RequirementQualityResponse | None:
        listed = await self.list_requirements(project_id, owner_id)
        if listed is None:
            return None
        requirements = list(
            await self.session.scalars(
                select(Requirement)
                .where(Requirement.project_id == project_id)
                .order_by(Requirement.requirement_code)
            )
        )
        conflicts = detect_conflicts([item.statement for item in requirements])
        ambiguity_count = 0
        conflict_count = 0
        for index, requirement in enumerate(requirements):
            findings = analyze_statement(requirement.statement, requirement.acceptance_criteria)
            findings.extend(conflicts.get(index, []))
            requirement.quality_findings = [finding.as_dict() for finding in findings]
            requirement.clarification_status = "required" if findings else "not_required"
            ambiguity_count += sum(finding.kind == "ambiguity" for finding in findings)
            conflict_count += sum(finding.kind == "conflict" for finding in findings)
        await self.session.commit()
        return RequirementQualityResponse(
            items=[RequirementResponse.model_validate(item) for item in requirements],
            ambiguity_count=ambiguity_count,
            conflict_count=conflict_count,
        )

    async def clarify(
        self,
        project_id: uuid.UUID,
        requirement_id: uuid.UUID,
        owner_id: uuid.UUID,
        data: RequirementClarificationInput,
    ) -> RequirementResponse | None:
        requirement = await self.session.scalar(
            select(Requirement)
            .join(Project, Project.id == Requirement.project_id)
            .where(
                Requirement.id == requirement_id,
                Requirement.project_id == project_id,
                Project.created_by_id == owner_id,
            )
        )
        if requirement is None:
            return None
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
        requirement.statement = data.statement.strip()
        requirement.acceptance_criteria = [item.strip() for item in data.acceptance_criteria]
        requirement.version += 1
        findings = analyze_statement(requirement.statement, requirement.acceptance_criteria)
        requirement.quality_findings = [finding.as_dict() for finding in findings]
        requirement.clarification_status = "required" if findings else "resolved"
        requirement.confidence = max(requirement.confidence, 0.9 if not findings else 0.7)
        AuditRepository(self.session).add(
            AuditEvent(
                project_id=project_id,
                actor_type="user",
                actor_id=owner_id,
                action="Clarified requirement",
                entity_type="requirement",
                entity_id=requirement.id,
                event_metadata={"version": requirement.version, "reason": data.reason},
            )
        )
        await self.session.commit()
        await self.session.refresh(requirement)
        return RequirementResponse.model_validate(requirement)
