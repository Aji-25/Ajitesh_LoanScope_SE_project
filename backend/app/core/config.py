from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "LoanScope API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = Field(min_length=1)
    cors_origins: str = "http://localhost:5173"
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=480, ge=5, le=1440)
    bootstrap_user_email: str | None = None
    bootstrap_user_password: str | None = Field(default=None, min_length=12)
    bootstrap_user_name: str = "Development analyst"
    llm_mode: Literal["mock", "openai", "gemini", "ollama", "hybrid"] = "ollama"
    llm_model: str = Field(default="gpt-4.1-mini", min_length=1)
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = Field(default="gemini-3.8-flash", min_length=1)
    ollama_base_url: str = Field(default="http://host.docker.internal:11434", min_length=1)
    ollama_model: str = Field(default="qwen3:4b", min_length=1)

    @field_validator("bootstrap_user_password", "openai_api_key", "gemini_api_key", mode="before")
    @classmethod
    def empty_optional_secret_is_unset(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator("llm_model", "gemini_model", "ollama_base_url", "ollama_model", mode="before")
    @classmethod
    def normalize_provider_setting(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().rstrip("/")
        return value

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
