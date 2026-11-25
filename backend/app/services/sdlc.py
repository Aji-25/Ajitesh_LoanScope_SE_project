import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AuditEvent, Project, SDLCRecommendation
from app.schemas.sdlc import ProjectCharacteristics, SDLCRecommendationResponse, SDLCScore

SCORING_VERSION = "3.0"
FACTORS = (
    "requirements_volatility",
    "compliance_criticality",
    "technical_risk",
    "customer_collaboration",
    "release_frequency",
    "team_experience",
)
# Each profile describes the conditions where that model is most suitable (1 to 5).
MODEL_PROFILES = {
    "waterfall": (1, 4, 2, 1, 1, 4),
    "v_shaped": (1, 5, 4, 2, 1, 4),
    "spiral": (5, 4, 5, 3, 2, 3),
    "prototype": (5, 1, 3, 5, 2, 2),
    "rapid_application_development": (4, 2, 2, 5, 5, 4),
    "iterative_incremental": (4, 3, 3, 3, 4, 3),
    "agile": (5, 2, 2, 5, 4, 4),
}
MODEL_LABELS = {
    "waterfall": "Waterfall model",
    "v_shaped": "V-shaped",
    "spiral": "Spiral",
    "prototype": "Prototype",
    "rapid_application_development": "Rapid application development (RAD)",
    "iterative_incremental": "Iterative/incremental",
    "agile": "Agile",
}


def score_sdlc(data: ProjectCharacteristics) -> SDLCScore:
    values = tuple(getattr(data, factor) for factor in FACTORS)
    normalized = {
        name: round(
            (
                1
                - sum(abs(actual - ideal) for actual, ideal in zip(values, profile, strict=True))
                / (len(FACTORS) * 4)
            )
            * 100,
            1,
        )
        for name, profile in MODEL_PROFILES.items()
    }
    recommendation = max(normalized, key=normalized.__getitem__)
    rationale = (
        f"{MODEL_LABELS[recommendation]} has the highest fit score "
        f"({normalized[recommendation]}%) across the six project characteristics "
        f"under scoring model {SCORING_VERSION}."
    )
    return SDLCScore(
        scores=normalized,
        recommendation=recommendation,
        rationale=rationale,
        scoring_version=SCORING_VERSION,
    )


class SDLCService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate(
        self, project_id: uuid.UUID, owner_id: uuid.UUID, data: ProjectCharacteristics
    ) -> SDLCRecommendationResponse | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        score = score_sdlc(data)
        record = SDLCRecommendation(
            project_id=project_id,
            characteristics=data.model_dump(),
            scores=score.scores,
            recommendation=score.recommendation,
            rationale=score.rationale,
            scoring_version=score.scoring_version,
        )
        self.session.add(record)
        await self.session.flush()
        self.session.add(
            AuditEvent(
                project_id=project_id,
                actor_type="system",
                agent_name="sdlc_engine",
                action="Created SDLC recommendation",
                entity_type="sdlc_recommendation",
                entity_id=record.id,
                event_metadata={
                    "recommendation": score.recommendation,
                    "scoring_version": score.scoring_version,
                },
            )
        )
        await self.session.commit()
        return SDLCRecommendationResponse.model_validate(record)

    async def latest(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> SDLCRecommendationResponse | None:
        record = await self.session.scalar(
            select(SDLCRecommendation)
            .join(Project)
            .where(
                SDLCRecommendation.project_id == project_id,
                SDLCRecommendation.scoring_version == SCORING_VERSION,
                Project.created_by_id == owner_id,
            )
            .order_by(SDLCRecommendation.created_at.desc())
            .limit(1)
        )
        return SDLCRecommendationResponse.model_validate(record) if record else None
