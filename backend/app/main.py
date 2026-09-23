from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.compliance import router as compliance_router
from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.projects import router as projects_router
from app.api.requirements import router as requirements_router
from app.api.workflows import router as workflows_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(health_router)
app.include_router(knowledge_router)
app.include_router(auth_router)
app.include_router(compliance_router)
app.include_router(projects_router)
app.include_router(requirements_router)
app.include_router(workflows_router)
