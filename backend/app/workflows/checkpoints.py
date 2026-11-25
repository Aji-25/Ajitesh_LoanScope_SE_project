from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.engine import make_url

from app.core.config import get_settings


def psycopg_database_url() -> str:
    database_url = make_url(get_settings().database_url).set(drivername="postgresql")
    return database_url.render_as_string(hide_password=False)


@asynccontextmanager
async def postgres_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    async with AsyncPostgresSaver.from_conn_string(psycopg_database_url()) as saver:
        await saver.setup()
        yield saver
