from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest
from app.services.auth import AuthService


def test_registration_normalizes_identity_fields() -> None:
    data = RegisterRequest(
        email="  Analyst@Example.com ",
        full_name="  Asha   Menon  ",
        password="StrongPassword9",
    )
    assert str(data.email) == "analyst@example.com"
    assert data.full_name == "Asha Menon"


@pytest.mark.parametrize(
    "password", ["short", "alllowercase123", "ALLUPPERCASE123", "NoNumbersHere"]
)
def test_registration_rejects_weak_passwords(password: str) -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(email="analyst@example.com", full_name="Asha Menon", password=password)


async def test_duplicate_registration_is_rejected() -> None:
    session = AsyncMock()
    service = AuthService(session)
    service.users.get_by_email = AsyncMock(return_value=object())  # type: ignore[method-assign]
    result = await service.register(
        RegisterRequest(
            email="analyst@example.com",
            full_name="Asha Menon",
            password="StrongPassword9",
        )
    )
    assert result is None
