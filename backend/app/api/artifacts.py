import uuid

from fastapi import APIRouter, HTTPException, Response

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.artifact import ArtifactList
from app.services.artifacts import ArtifactService

router = APIRouter(prefix="/projects/{project_id}/artifacts", tags=["artifacts"])


@router.get("", response_model=ArtifactList)
async def list_artifacts(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> ArtifactList:
    result = await ArtifactService(session).list(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/generate", response_model=ArtifactList)
async def generate_artifacts(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> ArtifactList:
    result = await ArtifactService(session).generate(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.get("/{artifact_id}/download")
async def download_artifact(
    project_id: uuid.UUID,
    artifact_id: uuid.UUID,
    user: CurrentUser,
    session: SessionDependency,
) -> Response:
    artifact = await ArtifactService(session).download(project_id, artifact_id, user.id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return Response(
        content=artifact.html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{artifact.artifact_type}.html"'},
    )
