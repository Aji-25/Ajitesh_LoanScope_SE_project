import html
import uuid
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    AuditEvent,
    ComplianceMapping,
    GeneratedArtifact,
    Project,
    Requirement,
    Risk,
    SDLCRecommendation,
)
from app.schemas.artifact import ArtifactList, ArtifactResponse
from app.services.sdlc import SCORING_VERSION


def render_html(title: str, sections: list[dict[str, Any]]) -> str:
    body = "".join(
        f"<section><h2>{html.escape(str(section['heading']))}</h2>"
        f"<pre>{html.escape(str(section['content']))}</pre></section>"
        for section in sections
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><style>body{{font-family:system-ui;"
        "max-width:900px;margin:40px auto;padding:0 24px;line-height:1.5}}"
        f"pre{{white-space:pre-wrap}}</style></head><body><h1>{html.escape(title)}</h1>"
        f"{body}</body></html>"
    )


def build_artifact_payloads(
    project: Project,
    requirements: list[Requirement],
    risks: list[Risk],
    compliance: list[ComplianceMapping],
    sdlc: SDLCRecommendation | None,
) -> list[tuple[str, str, list[dict[str, Any]]]]:
    rows = [
        {
            "id": item.requirement_code,
            "statement": item.statement,
            "source": item.source_stakeholder,
            "acceptance_criteria": item.acceptance_criteria,
            "status": item.approval_status,
        }
        for item in requirements
    ]
    traceability = [
        {
            "requirement_id": item.requirement_code,
            "source": item.source_stakeholder,
            "acceptance_criteria": item.acceptance_criteria,
            "compliance_mapping_ids": [
                str(mapping.id) for mapping in compliance if mapping.requirement_id == item.id
            ],
            "risk_ids": [risk.risk_code for risk in risks if risk.requirement_id == item.id],
        }
        for item in requirements
    ]
    requirement_codes = {item.id: item.requirement_code for item in requirements}
    return [
        (
            "srs",
            "Software Requirements Specification",
            [
                {"heading": "Project scope", "content": project.summary},
                {"heading": "Requirements", "content": rows},
            ],
        ),
        (
            "user_stories",
            "User Stories",
            [
                {
                    "heading": "Stories",
                    "content": [
                        {
                            "requirement_id": row["id"],
                            "story": "As a loan stakeholder, I need "
                            + str(row["statement"]).removeprefix("The system shall "),
                        }
                        for row in rows
                    ],
                }
            ],
        ),
        (
            "acceptance_criteria",
            "Acceptance Criteria",
            [
                {
                    "heading": "Criteria",
                    "content": [
                        {"requirement_id": row["id"], "criteria": row["acceptance_criteria"]}
                        for row in rows
                    ],
                }
            ],
        ),
        ("use_cases", "Use Cases", [{"heading": "Primary flows", "content": rows}]),
        (
            "risk_register",
            "Risk Register",
            [
                {
                    "heading": "Risks",
                    "content": [
                        {
                            "id": item.risk_code,
                            "requirement_id": (
                                requirement_codes.get(item.requirement_id)
                                if item.requirement_id is not None
                                else None
                            ),
                            "score": item.score,
                            "mitigation": item.mitigation,
                        }
                        for item in risks
                    ],
                }
            ],
        ),
        (
            "compliance_matrix",
            "Compliance Matrix",
            [
                {
                    "heading": "Mappings",
                    "content": [
                        {
                            "requirement_id": requirement_codes.get(
                                item.requirement_id, str(item.requirement_id)
                            ),
                            "obligation": item.obligation,
                            "citations": item.citations,
                        }
                        for item in compliance
                    ],
                }
            ],
        ),
        (
            "traceability_matrix",
            "Requirements Traceability Matrix",
            [{"heading": "Traceability", "content": traceability}],
        ),
        (
            "sdlc_report",
            "SDLC Recommendation Report",
            [
                {
                    "heading": "Recommendation",
                    "content": {
                        "method": sdlc.recommendation,
                        "scores": sdlc.scores,
                        "rationale": sdlc.rationale,
                    }
                    if sdlc
                    else {"status": "not calculated"},
                }
            ],
        ),
        (
            "open_issues",
            "Open Issues",
            [
                {
                    "heading": "Issues",
                    "content": [
                        {"requirement_id": item.requirement_code, "findings": item.quality_findings}
                        for item in requirements
                        if item.quality_findings
                    ],
                }
            ],
        ),
    ]


class ArtifactService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> ArtifactList | None:
        project = await self.session.scalar(
            select(Project).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        requirements = list(
            await self.session.scalars(
                select(Requirement)
                .where(Requirement.project_id == project_id)
                .order_by(Requirement.requirement_code)
            )
        )
        risks = list(await self.session.scalars(select(Risk).where(Risk.project_id == project_id)))
        compliance = list(
            await self.session.scalars(
                select(ComplianceMapping).where(ComplianceMapping.project_id == project_id)
            )
        )
        sdlc = await self.session.scalar(
            select(SDLCRecommendation)
            .where(
                SDLCRecommendation.project_id == project_id,
                SDLCRecommendation.scoring_version == SCORING_VERSION,
            )
            .order_by(SDLCRecommendation.created_at.desc())
            .limit(1)
        )
        version_rows = (
            await self.session.execute(
                select(GeneratedArtifact.artifact_type, func.max(GeneratedArtifact.version))
                .where(GeneratedArtifact.project_id == project_id)
                .group_by(GeneratedArtifact.artifact_type)
            )
        ).all()
        next_versions = {artifact_type: maximum + 1 for artifact_type, maximum in version_rows}
        artifacts: list[GeneratedArtifact] = []
        source_ids = [item.requirement_code for item in requirements]
        for artifact_type, title, sections in build_artifact_payloads(
            project, requirements, risks, compliance, sdlc
        ):
            artifact = GeneratedArtifact(
                project_id=project_id,
                artifact_type=artifact_type,
                title=title,
                content={"sections": sections},
                html_content=render_html(title, sections),
                source_requirement_ids=source_ids,
                version=next_versions.get(artifact_type, 1),
            )
            self.session.add(artifact)
            artifacts.append(artifact)
        await self.session.flush()
        for artifact in artifacts:
            self.session.add(
                AuditEvent(
                    project_id=project_id,
                    actor_type="system",
                    agent_name="documentation_service",
                    action="Generated project artefact",
                    entity_type="generated_artifact",
                    entity_id=artifact.id,
                    event_metadata={"artifact_type": artifact.artifact_type},
                )
            )
        await self.session.commit()
        return ArtifactList(items=[ArtifactResponse.model_validate(item) for item in artifacts])

    async def list(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> ArtifactList | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        items = list(
            await self.session.scalars(
                select(GeneratedArtifact)
                .where(GeneratedArtifact.project_id == project_id)
                .order_by(GeneratedArtifact.title)
            )
        )
        return ArtifactList(items=[ArtifactResponse.model_validate(item) for item in items])

    async def download(
        self, project_id: uuid.UUID, artifact_id: uuid.UUID, owner_id: uuid.UUID
    ) -> GeneratedArtifact | None:
        return cast(
            GeneratedArtifact | None,
            await self.session.scalar(
                select(GeneratedArtifact)
                .join(Project)
                .where(
                    GeneratedArtifact.id == artifact_id,
                    GeneratedArtifact.project_id == project_id,
                    Project.created_by_id == owner_id,
                )
            ),
        )
