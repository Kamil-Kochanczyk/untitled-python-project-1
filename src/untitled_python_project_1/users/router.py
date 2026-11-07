import datetime as dt
import uuid

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import UUID4

from untitled_python_project_1.users.schemas import (
    UserDBRow,
    UserGeneratedData,
    UserIn,
    UserOptionalIn,
    UserOut,
    UserProvidedData,
)
from untitled_python_project_1.users.utils import hash_password


def get_default_user_record() -> UserDBRow:
    return {
        "uuid4": uuid.uuid4(),
        "first_name": "doesnotexist",
        "surname": "doesnotexist",
        "username": "doesnotexist",
        "email": "does@not.exist",
        "hashed_password": hash_password(" "),
        "is_active": False,
        "created_at": dt.datetime.min.replace(tzinfo=dt.UTC),
        "modified_at": dt.datetime.min.replace(tzinfo=dt.UTC),
    }


def get_fake_users() -> dict[UUID4, UserDBRow]:
    fake_users: dict[UUID4, UserDBRow] = {}
    fake_uid = uuid.uuid4()
    fake_users[fake_uid] = {
        "uuid4": fake_uid,
        "first_name": "Łukasz María Jean-Luc",
        "surname": "François O'Connor",
        "username": "nioch000_",
        "email": "bob@minion.lepuczi",
        "hashed_password": hash_password("King Bob"),
        "is_active": True,
        "created_at": dt.datetime.now(tz=dt.UTC),
        "modified_at": dt.datetime.now(tz=dt.UTC),
    }
    return fake_users


mock_users = get_fake_users()

all_usernames = {user["username"] for user in mock_users.values()}

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_all_users() -> list[UserOut]:
    return [UserOut.model_validate(user_data) for user_data in mock_users.values()]


@router.get("/{uid}")
async def get_user(uid: UUID4) -> UserOut:
    return (
        UserOut.model_validate(mock_users[uid], extra="allow")
        if uid in mock_users
        else UserOut.model_validate(get_default_user_record())
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn) -> UserOut:
    if user.username in all_usernames:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username {user.username} already exists",
        )
    hashed_password = hash_password(user.password.get_secret_value())
    provided_data: UserProvidedData = {
        "first_name": user.first_name,
        "surname": user.surname,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
    }
    generated_data: UserGeneratedData = {
        "uuid4": uuid.uuid4(),
        "is_active": True,
        "created_at": dt.datetime.now(tz=dt.UTC),
        "modified_at": dt.datetime.now(tz=dt.UTC),
    }
    new_user_data: UserDBRow = {**provided_data, **generated_data}
    mock_users[new_user_data["uuid4"]] = new_user_data
    all_usernames.add(new_user_data["username"])
    return UserOut.model_validate(new_user_data, extra="allow")


@router.put("/{uid}")
async def update_user(uid: UUID4, updated_user: UserIn, response: Response) -> UserOut:
    if uid not in mock_users:
        response.status_code = status.HTTP_201_CREATED
        return await create_user(updated_user)

    hashed_password = hash_password(updated_user.password.get_secret_value())
    updated_data: UserProvidedData = {
        "first_name": updated_user.first_name,
        "surname": updated_user.surname,
        "username": updated_user.username,
        "email": updated_user.email,
        "hashed_password": hashed_password,
    }
    prev_data: UserDBRow = mock_users[uid]
    new_data: UserDBRow = {**prev_data, **updated_data}
    mock_users[uid] = new_data
    all_usernames.remove(prev_data["username"])
    all_usernames.add(new_data["username"])
    return UserOut.model_validate(new_data, extra="allow")


@router.patch("/{uid}")
async def partially_update_user(uid: UUID4, partially_updated_user: UserOptionalIn) -> UserOut:
    if uid not in mock_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with uid `{uid}` not found"
        )

    user_data = mock_users[uid]
    prev_username = user_data["username"]
    for key, value in partially_updated_user.model_dump().items():
        if value is not None:
            user_data[key] = value  # type: ignore[]
    mock_users[uid] = user_data
    new_username = user_data["username"]
    if new_username != prev_username:
        all_usernames.remove(prev_username)
        all_usernames.add(new_username)
    return UserOut.model_validate(user_data, extra="allow")


@router.delete("/{uid}")
async def delete_user(uid: UUID4) -> UserOut:
    if uid not in mock_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with uid `{uid}` not found"
        )

    deleted_user = mock_users.pop(uid)
    all_usernames.remove(deleted_user["username"])
    return UserOut.model_validate(deleted_user, extra="allow")
