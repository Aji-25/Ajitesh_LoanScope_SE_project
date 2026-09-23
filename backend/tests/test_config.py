from app.core.config import Settings


def test_allowed_origins_are_parsed_from_comma_separated_value() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://user:password@localhost/database",
        cors_origins="http://localhost:5173, https://clarifi.example",
    )

    assert settings.allowed_origins == [
        "http://localhost:5173",
        "https://clarifi.example",
    ]
