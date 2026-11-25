import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import Project, Requirement

PROJECT_LOAD_OPTIONS = (
    selectinload(Project.stakeholders),
    selectinload(Project.requirements.and_(Requirement.deleted_at.is_(None))),
)


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(self, user_id: uuid.UUID) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .options(*PROJECT_LOAD_OPTIONS)
            .where(Project.created_by_id == user_id)
            .order_by(Project.updated_at.desc())
        )
        return list(result.scalars().unique())

    async def get_for_user(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Project | None:
        result = await self.session.execute(
            select(Project)
            .options(*PROJECT_LOAD_OPTIONS)
            .where(Project.id == project_id, Project.created_by_id == user_id)
        )
        return result.scalar_one_or_none()

    def add(self, project: Project) -> None:
        self.session.add(project)
