import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import CurrentUser, SessionDependency
from app.schemas.knowledge import DocumentResponse, RetrievalRequest, RetrievalResponse
from app.services.knowledge import KnowledgeService

router = APIRouter(prefix="/projects/{project_id}/knowledge", tags=["knowledge"])


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: uuid.UUID,
    user: CurrentUser,
    session: SessionDependency,
    file: Annotated[UploadFile, File()],
    jurisdiction: Annotated[str, Form()],
    version: Annotated[str, Form()] = "1.0",
    effective_date: Annotated[datetime | None, Form()] = None,
) -> DocumentResponse:
    try:
        result = await KnowledgeService(session).upload(
            project_id, user.id, file, jurisdiction, version, effective_date
        )
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    project_id: uuid.UUID, user: CurrentUser, session: SessionDependency
) -> list[DocumentResponse]:
    result = await KnowledgeService(session).list_documents(project_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_evidence(
    project_id: uuid.UUID, data: RetrievalRequest, user: CurrentUser, session: SessionDependency
) -> RetrievalResponse:
    result = await KnowledgeService(session).retrieve(project_id, user.id, data.query, data.limit)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return result
