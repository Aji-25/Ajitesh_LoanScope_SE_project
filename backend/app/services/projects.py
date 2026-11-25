import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.audit import AuditRepository
from app.db.repositories.projects import ProjectRepository
from app.models.database import AuditEvent, Project, Stakeholder, User
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse


def to_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        summary=project.summary,
        product_type=project.product_type,
        jurisdiction=project.jurisdiction,
        status=project.status,
        current_stage=project.current_stage,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stakeholder_count=len(project.stakeholders),
        requirement_count=len(project.requirements),
    )


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.projects = ProjectRepository(session)
        self.audit = AuditRepository(session)

    async def list_projects(self, user_id: uuid.UUID) -> ProjectListResponse:
        projects = await self.projects.list_for_user(user_id)
        items = [to_project_response(project) for project in projects]
        return ProjectListResponse(items=items, total=len(items))

    async def get_project(
        self, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectResponse | None:
        project = await self.projects.get_for_user(project_id, user_id)
        return to_project_response(project) if project else None

    async def create_project(self, data: ProjectCreate, user: User) -> ProjectResponse:
        project = Project(
            name=data.name,
            summary=data.summary,
            product_type=data.product_type,
            jurisdiction=data.jurisdiction,
            created_by_id=user.id,
        )
        if data.primary_stakeholder:
            project.stakeholders.append(
                Stakeholder(
                    name=data.primary_stakeholder.name,
                    role=data.primary_stakeholder.role,
                    organization=data.primary_stakeholder.organization,
                )
            )
        self.projects.add(project)
        await self.session.flush()
        self.audit.add(
            AuditEvent(
                project_id=project.id,
                actor_type="human",
                actor_id=user.id,
                action=f"Created project {project.name}",
                entity_type="project",
                entity_id=project.id,
                event_metadata={"stage": project.current_stage},
            )
        )
        await self.session.commit()
        loaded_project = await self.projects.get_for_user(project.id, user.id)
        if loaded_project is None:
            raise RuntimeError("Created project could not be reloaded")
        return to_project_response(loaded_project)
