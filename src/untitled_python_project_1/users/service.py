import datetime as dt
import uuid
from typing import cast

from psycopg import AsyncConnection, sql
from psycopg.rows import class_row
from pydantic import UUID4

import untitled_python_project_1.users.constants as uc
from untitled_python_project_1.users.schemas import (
    UserDBRow,
    UserGeneratedData,
    UserIn,
    UserOptionalIn,
    UserOptionalProvidedData,
    UserOut,
    UserProvidedData,
)
from untitled_python_project_1.users.utils import (
    get_select_exists_query,
    hash_password,
    row_exists,
    row_exists_distinct_from,
)

# def get_mocked_user_database() -> dict[UUID4, UserDBRow]:
#     fake_users: dict[UUID4, UserDBRow] = {}
#     fake_uid = uuid.uuid4()
#     fake_users[fake_uid] = {
#         "uuid4": fake_uid,
#         "first_name": "Łukasz María Jean-Luc",
#         "surname": "François O'Connor",
#         "username": "nioch000_",
#         "email": "bob@minion.lepuczi",
#         "hashed_password": hash_password("King Bob"),
#         "is_active": True,
#         "created_at": dt.datetime.now(tz=dt.UTC),
#         "modified_at": dt.datetime.now(tz=dt.UTC),
#     }
#     return fake_users


async def create_users(async_connection: AsyncConnection) -> bool:
    async with async_connection.cursor() as acur:
        await acur.execute(sql.SQL(uc.TABLE_SQL_CREATE))
        query = sql.SQL("SELECT to_regclass('public.{table}') IS NOT NULL").format(
            table=sql.Identifier(uc.TABLE_NAME)
        )
        # print(query.as_string())
        await acur.execute(query)
        row = await acur.fetchone()
        if row is None:
            raise RuntimeError("Could not verify users table creation")
        return cast("bool", row[0])


async def get_all_users(async_connection: AsyncConnection) -> list[UserOut]:
    query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(uc.TABLE_NAME))
    # print(query.as_string())
    async with async_connection.cursor(row_factory=class_row(UserOut)) as acur:
        await acur.execute(query)
        return await acur.fetchall()


async def get_user(async_connection: AsyncConnection, uid: UUID4) -> UserOut | None:
    query = sql.SQL("SELECT * FROM {} where uid = %s").format(sql.Identifier(uc.TABLE_NAME))
    # print(query.as_string())
    async with async_connection.cursor(row_factory=class_row(UserOut)) as acur:
        await acur.execute(query, (uid,))
        return await acur.fetchone()


async def create_user(async_connection: AsyncConnection, user_in: UserIn) -> UserOut:
    hashed_password = hash_password(user_in.password.get_secret_value())
    provided_data: UserProvidedData = {
        "first_name": user_in.first_name,
        "surname": user_in.surname,
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": hashed_password,
    }
    generated_data: UserGeneratedData = {
        "uid": uuid.uuid4(),
        "is_active": True,
        "created_at": dt.datetime.now(tz=dt.UTC),
        "modified_at": dt.datetime.now(tz=dt.UTC),
    }
    new_user_data: UserDBRow = {**provided_data, **generated_data}
    query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholders}) RETURNING *").format(
        table=sql.Identifier(uc.TABLE_NAME),
        fields=sql.SQL(",").join([sql.Identifier(field_name) for field_name in new_user_data]),
        placeholders=sql.SQL(",").join(sql.Placeholder() * len(new_user_data)),
    )
    # print(query.as_string())
    async with async_connection.cursor(row_factory=class_row(UserOut)) as acur:
        await acur.execute(query, list(new_user_data.values()))
        row = await acur.fetchone()
        if row is None:
            raise AssertionError("INSERT ... RETURNING * returned None")
        return row


async def update_user(
    async_connection: AsyncConnection, uid: UUID4, updated_user: UserIn
) -> UserOut:
    hashed_password = hash_password(updated_user.password.get_secret_value())
    updated_data: UserProvidedData = {
        "first_name": updated_user.first_name,
        "surname": updated_user.surname,
        "username": updated_user.username,
        "email": updated_user.email,
        "hashed_password": hashed_password,
    }
    final_data = {**updated_data}
    final_data["modified_at"] = dt.datetime.now(tz=dt.UTC)
    query = sql.SQL("UPDATE {table} SET {kvpairs} WHERE uid=%s RETURNING *").format(
        table=sql.Identifier(uc.TABLE_NAME),
        kvpairs=sql.SQL(",").join(
            sql.SQL("=").join([sql.Identifier(field_name), sql.Placeholder()])
            for field_name in final_data
        ),
    )
    # print(query.as_string())
    async with async_connection.cursor(row_factory=class_row(UserOut)) as acur:
        await acur.execute(query, [*final_data.values(), uid])
        row = await acur.fetchone()
        if row is None:
            # we assume that the case with non-existent UID is handled in the dependencies.py
            raise AssertionError("UPDATE ... RETURNING * returned None")
        return row


async def partially_update_user(
    async_connection: AsyncConnection, uid: UUID4, partially_updated_user: UserOptionalIn
) -> UserOut:
    hashed_password = (
        hash_password(partially_updated_user.password.get_secret_value())
        if partially_updated_user.password is not None
        else None
    )
    partially_updated_data: UserOptionalProvidedData = {
        "first_name": partially_updated_user.first_name,
        "surname": partially_updated_user.surname,
        "username": partially_updated_user.username,
        "email": partially_updated_user.email,
        "hashed_password": hashed_password,
    }
    not_none = {k: v for k, v in partially_updated_data.items() if v is not None}
    not_none["modified_at"] = dt.datetime.now(tz=dt.UTC)
    query = sql.SQL("UPDATE {table} SET {kvpairs} WHERE uid=%s RETURNING *").format(
        table=sql.Identifier(uc.TABLE_NAME),
        kvpairs=sql.SQL(",").join(
            sql.SQL("=").join([sql.Identifier(field_name), sql.Placeholder()])
            for field_name in not_none
        ),
    )
    # print(query.as_string())
    async with async_connection.cursor(row_factory=class_row(UserOut)) as acur:
        await acur.execute(query, [*not_none.values(), uid])
        row = await acur.fetchone()
        if row is None:
            # we assume that case with non-existent UID is handled in the dependencies.py
            raise AssertionError("UPDATE ... RETURNING * returned None")
        return row


async def delete_user(async_connection: AsyncConnection, uid: UUID4) -> UserOut:
    query = sql.SQL("DELETE FROM {table} where uid=%s RETURNING *").format(
        table=sql.Identifier(uc.TABLE_NAME)
    )
    # print(query.as_string())
    async with async_connection.cursor(row_factory=class_row(UserOut)) as acur:
        await acur.execute(query, (uid,))
        row = await acur.fetchone()
        if row is None:
            # we assume that case with non-existent UID is handled in the dependencies.py
            raise AssertionError("DELETE ... RETURNING * returned None")
        return row


async def is_username_taken(
    async_connection: AsyncConnection, username: str, existing_uid: UUID4 | None
) -> bool:
    return await row_exists_distinct_from(
        async_connection,
        get_select_exists_query(uc.TABLE_NAME, "username", distinct_from="uid"),
        username,
        existing_uid,
    )


async def is_email_taken(
    async_connection: AsyncConnection, email: str, existing_uid: UUID4 | None
) -> bool:
    return await row_exists_distinct_from(
        async_connection,
        get_select_exists_query(uc.TABLE_NAME, "email", distinct_from="uid"),
        email,
        existing_uid,
    )


async def uid_exists(async_connection: AsyncConnection, uid: UUID4) -> bool:
    return await row_exists(async_connection, get_select_exists_query(uc.TABLE_NAME, "uid"), uid)
