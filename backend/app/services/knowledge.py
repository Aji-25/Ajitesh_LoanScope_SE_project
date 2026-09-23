import hashlib
import io
import math
import re
import uuid
from datetime import datetime

from docx import Document as DocxDocument
from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import DocumentChunk, KnowledgeDocument, Project
from app.schemas.knowledge import DocumentResponse, EvidenceChunk, RetrievalResponse

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, size: int = 180, overlap: int = 30) -> list[str]:
    words = clean_text(text).split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, size - overlap)
    for start in range(0, len(words), step):
        chunk = words[start : start + size]
        if chunk:
            chunks.append(" ".join(chunk))
        if start + size >= len(words):
            break
    return chunks


def deterministic_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += -1.0 if digest[4] & 1 else 1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def parse_content(data: bytes, content_type: str) -> tuple[str, int]:
    if content_type == "application/pdf":
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages), len(reader.pages)
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document = DocxDocument(io.BytesIO(data))
        return "\n".join(paragraph.text for paragraph in document.paragraphs), 1
    return data.decode("utf-8"), 1


class KnowledgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upload(
        self,
        project_id: uuid.UUID,
        owner_id: uuid.UUID,
        file: UploadFile,
        jurisdiction: str,
        version: str,
        effective_date: datetime | None,
    ) -> DocumentResponse | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError("Only PDF, DOCX, and UTF-8 text files are supported.")
        data = await file.read()
        if len(data) > 10 * 1024 * 1024:
            raise ValueError("Documents must be 10 MB or smaller.")
        text, page_count = parse_content(data, content_type)
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("The document does not contain extractable text.")
        document = KnowledgeDocument(
            project_id=project_id,
            filename=file.filename or "document",
            content_type=content_type,
            version=version,
            jurisdiction=jurisdiction,
            effective_date=effective_date,
            page_count=page_count,
        )
        self.session.add(document)
        await self.session.flush()
        for index, content in enumerate(chunks):
            self.session.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    page_number=min(index + 1, page_count),
                    section=f"Chunk {index + 1}",
                    token_count=len(content.split()),
                    embedding=deterministic_embedding(content),
                    chunk_metadata={
                        "filename": document.filename,
                        "version": version,
                        "jurisdiction": jurisdiction,
                    },
                )
            )
        await self.session.commit()
        return DocumentResponse.model_validate(document)

    async def list_documents(
        self, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> list[DocumentResponse] | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        items = list(
            await self.session.scalars(
                select(KnowledgeDocument)
                .where(KnowledgeDocument.project_id == project_id)
                .order_by(KnowledgeDocument.created_at.desc())
            )
        )
        return [DocumentResponse.model_validate(item) for item in items]

    async def retrieve(
        self, project_id: uuid.UUID, owner_id: uuid.UUID, query: str, limit: int
    ) -> RetrievalResponse | None:
        project = await self.session.scalar(
            select(Project.id).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        distance = DocumentChunk.embedding.cosine_distance(deterministic_embedding(query))
        rows = (
            await self.session.execute(
                select(DocumentChunk, KnowledgeDocument, distance.label("distance"))
                .join(KnowledgeDocument)
                .where(KnowledgeDocument.project_id == project_id)
                .order_by(distance)
                .limit(limit)
            )
        ).all()
        return RetrievalResponse(
            items=[
                EvidenceChunk(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    filename=document.filename,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    version=document.version,
                    jurisdiction=document.jurisdiction,
                    effective_date=document.effective_date,
                    score=max(0.0, 1.0 - float(item_distance)),
                )
                for chunk, document, item_distance in rows
            ]
        )
