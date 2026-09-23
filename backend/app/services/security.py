import uuid
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Project, Requirement, Risk, SecurityFinding
from app.schemas.security import RiskResponse, SecurityFindingResponse, SecurityRiskResponse


@dataclass(frozen=True)
class SecurityAssessment:
    category: str
    severity: str
    title: str
    description: str
    recommendation: str
    likelihood: int
    impact: int


def assess_security(statement: str, categories: list[str]) -> list[SecurityAssessment]:
    lowered = statement.lower()
    output: list[SecurityAssessment] = []
    if "upload" in lowered or "document" in lowered:
        output.append(
            SecurityAssessment(
                "data_protection",
                "high",
                "Protect uploaded evidence",
                "Applicant documents may expose sensitive personal and financial data.",
                "Encrypt objects, scan uploads, enforce least privilege, and define "
                "retention deletion.",
                3,
                5,
            )
        )
    if "access" in lowered or "authenticate" in lowered or "security" in categories:
        output.append(
            SecurityAssessment(
                "access_control",
                "high",
                "Enforce controlled access",
                "Unauthorized access could expose or alter loan decisions.",
                "Use phishing-resistant MFA, role-based authorization, session limits, "
                "and audit events.",
                3,
                5,
            )
        )
    if "decision" in lowered or "score" in lowered:
        output.append(
            SecurityAssessment(
                "integrity",
                "medium",
                "Protect decision integrity",
                "Tampering or untraceable model changes can alter lending outcomes.",
                "Version decision inputs and rules, require approvals, and monitor "
                "anomalous changes.",
                2,
                5,
            )
        )
    return output


class SecurityRiskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> SecurityRiskResponse | None:
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
            delete(SecurityFinding).where(SecurityFinding.project_id == project_id)
        )
        await self.session.execute(delete(Risk).where(Risk.project_id == project_id))
        findings: list[SecurityFinding] = []
        risks: list[Risk] = []
        for requirement in requirements:
            for assessment in assess_security(requirement.statement, requirement.categories):
                finding = SecurityFinding(
                    project_id=project_id,
                    requirement_id=requirement.id,
                    category=assessment.category,
                    title=assessment.title,
                    description=assessment.description,
                    severity=assessment.severity,
                    recommendation=assessment.recommendation,
                )
                self.session.add(finding)
                findings.append(finding)
                risk = Risk(
                    project_id=project_id,
                    requirement_id=requirement.id,
                    risk_code=f"RSK-{len(risks) + 1:03d}",
                    category=assessment.category,
                    description=assessment.description,
                    likelihood=assessment.likelihood,
                    impact=assessment.impact,
                    score=assessment.likelihood * assessment.impact,
                    mitigation=assessment.recommendation,
                    owner_role="Security Reviewer",
                )
                self.session.add(risk)
                risks.append(risk)
        await self.session.commit()
        return SecurityRiskResponse(
            findings=[SecurityFindingResponse.model_validate(item) for item in findings],
            risks=[RiskResponse.model_validate(item) for item in risks],
        )

    async def list(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> SecurityRiskResponse | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        findings = list(
            await self.session.scalars(
                select(SecurityFinding)
                .where(SecurityFinding.project_id == project_id)
                .order_by(SecurityFinding.created_at)
            )
        )
        risks = list(
            await self.session.scalars(
                select(Risk).where(Risk.project_id == project_id).order_by(Risk.risk_code)
            )
        )
        return SecurityRiskResponse(
            findings=[SecurityFindingResponse.model_validate(item) for item in findings],
            risks=[RiskResponse.model_validate(item) for item in risks],
        )
