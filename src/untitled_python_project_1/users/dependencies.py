from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4

from untitled_python_project_1.users.exceptions import (
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from untitled_python_project_1.users.schemas import UserIn, UserOptionalIn, UserOut
from untitled_python_project_1.users.service import MockedUserDatabaseSession


async def get_user_database_session() -> AsyncGenerator[MockedUserDatabaseSession, None]:
    mocked_user_db_session = MockedUserDatabaseSession()
    try:
        yield mocked_user_db_session
    finally:
        mocked_user_db_session.close()


async def get_user_by_uid(
    uid: UUID4,
    user_db_session: Annotated[MockedUserDatabaseSession, Depends(get_user_database_session)],
) -> UserOut:
    user = await user_db_session.get_user_by_uid(uid)
    if user is None:
        raise UserNotFoundError(uid)
    return user


async def get_user_with_valid_username(
    user_in: UserIn,
    user_db_session: Annotated[MockedUserDatabaseSession, Depends(get_user_database_session)],
) -> UserIn:
    username = user_in.username
    is_username_invalid = await user_db_session.is_username_invalid(username)
    if is_username_invalid:
        raise UsernameAlreadyExistsError(username)
    return user_in


async def get_user_with_valid_username_optional(
    user_optional_in: UserOptionalIn,
    user_db_session: Annotated[MockedUserDatabaseSession, Depends(get_user_database_session)],
) -> UserOptionalIn:
    username = user_optional_in.username
    if username is not None:
        is_username_invalid = await user_db_session.is_username_invalid(username)
        if is_username_invalid:
            raise UsernameAlreadyExistsError(username)
    return user_optional_in


async def get_existing_uid(
    uid: UUID4,
    user_db_session: Annotated[MockedUserDatabaseSession, Depends(get_user_database_session)],
) -> UUID4 | None:
    uid_exists = await user_db_session.uid_exists(uid)
    return uid if uid_exists else None
