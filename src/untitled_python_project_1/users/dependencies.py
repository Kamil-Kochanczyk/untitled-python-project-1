from typing import Annotated

from fastapi import Depends, HTTPException, status
from psycopg import AsyncConnection
from pydantic import UUID4

import untitled_python_project_1.users.service as us
from untitled_python_project_1.dependencies import get_async_connection
from untitled_python_project_1.users.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from untitled_python_project_1.users.schemas import UserIn, UserOptionalIn, UserOut


async def get_user_by_uid(
    uid: UUID4,
    async_connection: Annotated[AsyncConnection, Depends(get_async_connection)],
) -> UserOut:
    user = await us.get_user(async_connection, uid)
    if user is None:
        raise UserNotFoundError(uid)
    return user


async def get_existing_uid(
    async_connection: Annotated[AsyncConnection, Depends(get_async_connection)],
    uid: UUID4 | None = None,
) -> UUID4 | None:
    # provide default None value for uid
    # this doesn't make FastAPI go crazy if it can't find uid in the endpoint path
    if uid is None:
        return None
    uid_exists = await us.uid_exists(async_connection, uid)
    return uid if uid_exists else None


async def get_user_with_valid_username(
    user_in: UserIn,
    async_connection: Annotated[AsyncConnection, Depends(get_async_connection)],
    existing_uid: Annotated[UUID4 | None, Depends(get_existing_uid)],
) -> UserIn:
    username = user_in.username
    is_username_invalid = await us.is_username_taken(async_connection, username, existing_uid)
    if is_username_invalid:
        raise UsernameAlreadyExistsError(username)
    return user_in


async def get_user_with_valid_email(
    user_in: Annotated[UserIn, Depends(get_user_with_valid_username)],
    async_connection: Annotated[AsyncConnection, Depends(get_async_connection)],
    existing_uid: Annotated[UUID4 | None, Depends(get_existing_uid)],
) -> UserIn:
    email = user_in.email
    is_email_invalid = await us.is_email_taken(async_connection, email, existing_uid)
    if is_email_invalid:
        raise EmailAlreadyExistsError(email)
    return user_in


async def get_user_with_valid_username_optional(
    user_optional_in: UserOptionalIn,
    async_connection: Annotated[AsyncConnection, Depends(get_async_connection)],
    existing_uid: Annotated[UUID4 | None, Depends(get_existing_uid)],
) -> UserOptionalIn:
    username = user_optional_in.username
    if username is not None:
        is_username_invalid = await us.is_username_taken(async_connection, username, existing_uid)
        if is_username_invalid:
            raise UsernameAlreadyExistsError(username)
    return user_optional_in


async def get_user_with_valid_email_optional(
    user_optional_in: Annotated[UserOptionalIn, Depends(get_user_with_valid_username_optional)],
    async_connection: Annotated[AsyncConnection, Depends(get_async_connection)],
    existing_uid: Annotated[UUID4 | None, Depends(get_existing_uid)],
) -> UserOptionalIn:
    email = user_optional_in.email
    if email is not None:
        is_email_invalid = await us.is_email_taken(async_connection, email, existing_uid)
        if is_email_invalid:
            raise EmailAlreadyExistsError(email)
    if all(v is None for v in user_optional_in.model_dump().values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="No data provided"
        )
    return user_optional_in
