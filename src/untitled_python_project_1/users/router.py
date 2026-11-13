from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from psycopg import AsyncConnection
from pydantic import UUID4

import untitled_python_project_1.users.service as us
from untitled_python_project_1.dependencies import get_async_connection
from untitled_python_project_1.users.dependencies import (
    get_existing_uid,
    get_user_by_uid,
    get_user_with_valid_email,
    get_user_with_valid_email_optional,
)
from untitled_python_project_1.users.schemas import (
    UserIn,
    UserOptionalIn,
    UserOut,
)

type AsyncConnectionDep = Annotated[AsyncConnection, Depends(get_async_connection)]
type ExistingUIDDep = Annotated[UUID4 | None, Depends(get_existing_uid)]
type ValidUsernameAndEmailDep = Annotated[UserIn, Depends(get_user_with_valid_email)]
type ValidOptionalUsernameAndEmailDep = Annotated[
    UserOptionalIn, Depends(get_user_with_valid_email_optional)
]


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_all_users(async_connection: AsyncConnectionDep) -> list[UserOut]:
    return await us.get_all_users(async_connection)


@router.get("/{uid}")
async def get_user(user_out: Annotated[UserOut, Depends(get_user_by_uid)]) -> UserOut:
    return user_out


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: ValidUsernameAndEmailDep, async_connection: AsyncConnectionDep
) -> UserOut:
    return await us.create_user(async_connection, user_in)


@router.put("/{uid}")
async def update_user(
    uid: ExistingUIDDep,
    updated_user: ValidUsernameAndEmailDep,
    async_connection: AsyncConnectionDep,
    response: Response,
) -> UserOut:
    if uid is None:
        response.status_code = status.HTTP_201_CREATED
        return await us.create_user(async_connection, updated_user)
    return await us.update_user(async_connection, uid, updated_user)


@router.patch("/{uid}")
async def partially_update_user(
    uid: ExistingUIDDep,
    partially_updated_user: ValidOptionalUsernameAndEmailDep,
    async_connection: AsyncConnectionDep,
) -> UserOut:
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot update user with the given uid: such user doesn't exist",
        )
    return await us.partially_update_user(async_connection, uid, partially_updated_user)


@router.delete("/{uid}")
async def delete_user(uid: ExistingUIDDep, async_connection: AsyncConnectionDep) -> UserOut:
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot delete user with the given uid: such user doesn't exist",
        )
    return await us.delete_user(async_connection, uid)
