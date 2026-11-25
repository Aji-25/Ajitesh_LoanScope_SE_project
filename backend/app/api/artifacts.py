import uuid

from fastapi import APIRouter, HTTPException, Response
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.artifact import ArtifactList
from app.services.artifact_pdf import render_artifact_pdf
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
    pdf = await run_in_threadpool(
        render_artifact_pdf, artifact.title, artifact.version, artifact.content["sections"]
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{artifact.artifact_type}.pdf"'},
    )
