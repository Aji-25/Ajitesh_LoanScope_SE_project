from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_allowed_origins_are_parsed_from_comma_separated_value() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://user:password@localhost/database",
        cors_origins="http://localhost:5173, https://loanscope.example",
    )

    assert settings.allowed_origins == [
        "http://localhost:5173",
        "https://loanscope.example",
    ]


def test_empty_optional_bootstrap_password_is_treated_as_unset() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://user:password@localhost/database",
        jwt_secret="a-secret-that-is-at-least-thirty-two-characters",
        bootstrap_user_password="",
    )

    assert settings.bootstrap_user_password is None


def test_provider_configuration_is_normalized() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://user:password@localhost/database",
        jwt_secret="a-secret-that-is-at-least-thirty-two-characters",
        llm_mode="hybrid",
        gemini_api_key="test-key",
        gemini_model=" gemini-3.8-flash ",
        ollama_base_url="http://host.docker.internal:11434/",
        ollama_model=" qwen3:4b ",
    )

    assert settings.gemini_model == "gemini-3.8-flash"
    assert settings.ollama_base_url == "http://host.docker.internal:11434"
    assert settings.ollama_model == "qwen3:4b"


@pytest.mark.parametrize("field", ["gemini_model", "ollama_base_url", "ollama_model"])
def test_provider_configuration_rejects_empty_required_values(field: str) -> None:
    values: dict[str, Any] = {
        "database_url": "postgresql+asyncpg://user:password@localhost/database",
        "jwt_secret": "a-secret-that-is-at-least-thirty-two-characters",
        field: "   ",
    }
    with pytest.raises(ValidationError):
        Settings(**values)
