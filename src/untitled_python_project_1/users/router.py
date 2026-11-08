from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import UUID4

from untitled_python_project_1.users.dependencies import (
    get_existing_uid,
    get_user_by_uid,
    get_user_database_session,
    get_user_with_valid_username,
    get_user_with_valid_username_optional,
)
from untitled_python_project_1.users.schemas import (
    UserIn,
    UserOptionalIn,
    UserOut,
)
from untitled_python_project_1.users.service import MockedUserDatabaseSession

type UserDatabaseSessionDep = Annotated[
    MockedUserDatabaseSession, Depends(get_user_database_session)
]
type ValidUsernameDep = Annotated[UserIn, Depends(get_user_with_valid_username)]
type ValidOptionalUsernameDep = Annotated[
    UserOptionalIn, Depends(get_user_with_valid_username_optional)
]
type ExistingUIDDep = Annotated[UUID4 | None, Depends(get_existing_uid)]


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_all_users(user_database_session: UserDatabaseSessionDep) -> list[UserOut]:
    return await user_database_session.get_all_users()


@router.get("/{uid}")
async def get_user(user_out: Annotated[UserOut, Depends(get_user_by_uid)]) -> UserOut:
    return user_out


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: ValidUsernameDep, user_database_session: UserDatabaseSessionDep
) -> UserOut:
    return await user_database_session.create_user(user_in)


@router.put("/{uid}")
async def update_user(
    uid: ExistingUIDDep,
    updated_user: ValidUsernameDep,
    user_database_session: UserDatabaseSessionDep,
    response: Response,
) -> UserOut:
    if uid is None:
        response.status_code = status.HTTP_201_CREATED
        return await user_database_session.create_user(updated_user)
    return await user_database_session.update_user(uid, updated_user)


@router.patch("/{uid}")
async def partially_update_user(
    uid: ExistingUIDDep,
    partially_updated_user: ValidOptionalUsernameDep,
    user_database_session: UserDatabaseSessionDep,
) -> UserOut:
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot update user with the given uid: such user doesn't exist",
        )
    return await user_database_session.pariatlly_update_user(uid, partially_updated_user)


@router.delete("/{uid}")
async def delete_user(
    uid: ExistingUIDDep, user_database_session: UserDatabaseSessionDep
) -> UserOut:
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot delete user with the given uid: such user doesn't exist",
        )
    return await user_database_session.delete_user(uid)
