from types import SimpleNamespace

import pytest
from psycopg.conninfo import conninfo_to_dict

from app.workflows import checkpoints


def test_psycopg_database_url_encodes_reserved_password_characters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        checkpoints,
        "get_settings",
        lambda: SimpleNamespace(
            database_url=(
                "postgresql+asyncpg://loanscope_user:"
                "password-with:colon+plus@postgres:5432/loanscope_database"
            )
        ),
    )

    parsed = conninfo_to_dict(checkpoints.psycopg_database_url())

    assert parsed["user"] == "loanscope_user"
    assert parsed["password"] == "password-with:colon+plus"
    assert parsed["host"] == "postgres"
    assert parsed["port"] == "5432"
    assert parsed["dbname"] == "loanscope_database"
