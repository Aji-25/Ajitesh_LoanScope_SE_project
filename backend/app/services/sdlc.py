import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Project, SDLCRecommendation
from app.schemas.sdlc import ProjectCharacteristics, SDLCRecommendationResponse, SDLCScore


def score_sdlc(data: ProjectCharacteristics) -> SDLCScore:
    v, c, r, collaboration, frequency, experience = (
        data.requirements_volatility,
        data.compliance_criticality,
        data.technical_risk,
        data.customer_collaboration,
        data.release_frequency,
        data.team_experience,
    )
    scores = {
        "agile": 2 * v + 2 * collaboration + 2 * frequency + experience - c,
        "waterfall": 2 * (6 - v) + 2 * c + (6 - frequency) + experience,
        "spiral": 2 * r + c + v + experience,
        "v_model": 2 * c + 3 * r + (6 - v) + experience,
    }
    normalized = {name: round(value / 40 * 100, 1) for name, value in scores.items()}
    recommendation = max(normalized, key=normalized.__getitem__)
    rationale = (
        f"{recommendation.replace('_', ' ').title()} has the highest deterministic fit "
        f"score ({normalized[recommendation]}%) under scoring model 1.0."
    )
    return SDLCScore(scores=normalized, recommendation=recommendation, rationale=rationale)


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
        await self.session.commit()
        return SDLCRecommendationResponse.model_validate(record)

    async def latest(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> SDLCRecommendationResponse | None:
        record = await self.session.scalar(
            select(SDLCRecommendation)
            .join(Project)
            .where(SDLCRecommendation.project_id == project_id, Project.created_by_id == owner_id)
            .order_by(SDLCRecommendation.created_at.desc())
            .limit(1)
        )
        return SDLCRecommendationResponse.model_validate(record) if record else None
