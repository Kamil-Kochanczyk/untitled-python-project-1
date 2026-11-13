import hashlib
from typing import Any, cast

from psycopg import AsyncConnection, sql


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_select_exists_query(
    table_name: str, field_name: str, distinct_from: str | None = None
) -> sql.Composed:
    if distinct_from is not None:
        return sql.SQL(
            "SELECT EXISTS (SELECT 1 FROM {table} WHERE {field}={placeholder} AND {dfield} IS DISTINCT FROM {dplaceholder})"
        ).format(
            table=sql.Identifier(table_name),
            field=sql.Identifier(field_name),
            placeholder=sql.Placeholder(),
            dfield=sql.Identifier(distinct_from),
            dplaceholder=sql.Placeholder(),
        )
    return sql.SQL("SELECT EXISTS (SELECT 1 FROM {table} WHERE {field}={placeholder})").format(
        table=sql.Identifier(table_name),
        field=sql.Identifier(field_name),
        placeholder=sql.Placeholder(),
    )


async def row_exists(
    async_connection: AsyncConnection,
    select_exists_query: sql.Composed,
    field_value: Any,
) -> bool:
    # quick boolean exist check using SELECT EXIST ...

    async with async_connection.cursor() as acur:
        await acur.execute(select_exists_query, (field_value,))
        row = await acur.fetchone()

    if row is None:
        raise AssertionError("SELECT EXISTS ... returned None")

    return cast("bool", row[0])


async def row_exists_distinct_from(
    async_connection: AsyncConnection,
    select_exists_distinct_from_query: sql.Composed,
    field_value: Any,
    dfield_value: Any,
) -> bool:
    # quick boolean exist check using SELECT EXIST ... WHERE ... IS DISTINCT FROM ...

    async with async_connection.cursor() as acur:
        await acur.execute(select_exists_distinct_from_query, (field_value, dfield_value))
        row = await acur.fetchone()

    if row is None:
        raise AssertionError("SELECT EXIST ... WHERE ... IS DISTINCT FROM ... returned None")

    return cast("bool", row[0])
