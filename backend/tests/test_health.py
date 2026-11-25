from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch

from app.db import session as database_session
from app.main import app


async def test_liveness_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_endpoint_when_database_is_connected(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("app.api.health.database_is_ready", AsyncMock(return_value=True))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


async def test_readiness_endpoint_when_database_is_unavailable(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.api.health.database_is_ready", AsyncMock(return_value=False))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "disconnected"}


async def test_database_readiness_handles_connection_resolution_failure(
    monkeypatch: MonkeyPatch,
) -> None:
    class UnavailableEngine:
        def connect(self) -> None:
            raise OSError("database hostname is unavailable")

    monkeypatch.setattr(database_session, "engine", UnavailableEngine())

    assert await database_session.database_is_ready() is False
