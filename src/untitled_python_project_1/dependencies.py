from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Request
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from untitled_python_project_1.config import GlobalSettings


@lru_cache
def get_global_settings() -> GlobalSettings:
    return GlobalSettings()  # type: ignore[]


async def get_async_connection(request: Request) -> AsyncGenerator[AsyncConnection]:
    apool: AsyncConnectionPool = request.app.state.apool
    async with apool.connection() as aconn:
        yield aconn
