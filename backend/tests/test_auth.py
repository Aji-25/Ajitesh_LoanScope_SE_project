import uuid
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch

from app.main import app
from app.models.database import Role, User
from app.models.domain import RoleName
from app.services.auth import (
    AuthService,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_can_be_verified_without_storing_plaintext() -> None:
    encoded = hash_password("a-local-password-for-tests")

    assert encoded != "a-local-password-for-tests"
    assert verify_password("a-local-password-for-tests", encoded)
    assert not verify_password("incorrect-password", encoded)


def test_access_token_round_trip() -> None:
    user_id = uuid.uuid4()

    token = create_access_token(user_id)

    assert decode_access_token(token) == user_id
    assert decode_access_token(f"{token}invalid") is None


async def test_protected_route_rejects_anonymous_request() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/projects")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication is required."


async def test_login_returns_user_and_bearer_token(monkeypatch: MonkeyPatch) -> None:
    user = User(
        id=uuid.uuid4(),
        email="priya.raman@example.com",
        full_name="Priya Raman",
        password_hash="not-used-in-this-api-test",
        role_id=uuid.uuid4(),
        role=Role(
            id=uuid.uuid4(),
            name=RoleName.BUSINESS_ANALYST,
            description="Creates requirement projects",
        ),
    )
    monkeypatch.setattr(AuthService, "authenticate", AsyncMock(return_value=user))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "priya.raman@example.com", "password": "local-password"},
        )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["user"]["role"] == RoleName.BUSINESS_ANALYST
