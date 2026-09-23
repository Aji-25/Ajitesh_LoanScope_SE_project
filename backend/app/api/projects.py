import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, SessionDependency
from app.models.domain import RoleName
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse
from app.services.projects import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
PROJECT_CREATORS = {
    RoleName.ADMIN,
    RoleName.BUSINESS_ANALYST,
    RoleName.PROJECT_MANAGER,
}


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    user: CurrentUser,
    session: SessionDependency,
) -> ProjectResponse:
    if user.role.name not in PROJECT_CREATORS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role cannot create projects.",
        )
    return await ProjectService(session).create_project(data, user)


@router.get("", response_model=ProjectListResponse)
async def list_projects(user: CurrentUser, session: SessionDependency) -> ProjectListResponse:
    return await ProjectService(session).list_projects(user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    user: CurrentUser,
    session: SessionDependency,
) -> ProjectResponse:
    project = await ProjectService(session).get_project(project_id, user.id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    return project
