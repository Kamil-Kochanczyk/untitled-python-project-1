import datetime as dt
import uuid

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


def get_mocked_user_database() -> dict[UUID4, UserDBRow]:
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


mocked_user_database = get_mocked_user_database()


class MockedUserDatabaseSession:
    def __init__(self) -> None:
        self.db = mocked_user_database
        self.all_usernames = {user["username"] for user in self.db.values()}
        self.is_connected = True

    def close(self) -> None:
        self.is_connected = False

    async def is_username_invalid(self, username: str) -> bool:
        return username in self.all_usernames

    async def uid_exists(self, uid: UUID4) -> bool:
        return uid in self.db

    async def get_all_users(self) -> list[UserOut]:
        return [UserOut.model_validate(user_data) for user_data in self.db.values()]

    async def get_user_by_uid(self, uid: UUID4) -> UserOut | None:
        user = self.db.get(uid, None)
        return UserOut.model_validate(user, extra="allow") if user is not None else None

    async def create_user(self, user_in: UserIn) -> UserOut:
        hashed_password = hash_password(user_in.password.get_secret_value())
        provided_data: UserProvidedData = {
            "first_name": user_in.first_name,
            "surname": user_in.surname,
            "username": user_in.username,
            "email": user_in.email,
            "hashed_password": hashed_password,
        }
        generated_data: UserGeneratedData = {
            "uuid4": uuid.uuid4(),
            "is_active": True,
            "created_at": dt.datetime.now(tz=dt.UTC),
            "modified_at": dt.datetime.now(tz=dt.UTC),
        }
        new_user_data: UserDBRow = {**provided_data, **generated_data}
        self.db[new_user_data["uuid4"]] = new_user_data
        self.all_usernames.add(new_user_data["username"])
        return UserOut.model_validate(new_user_data, extra="allow")

    async def update_user(self, uid: UUID4, updated_user: UserIn) -> UserOut:
        hashed_password = hash_password(updated_user.password.get_secret_value())
        updated_data: UserProvidedData = {
            "first_name": updated_user.first_name,
            "surname": updated_user.surname,
            "username": updated_user.username,
            "email": updated_user.email,
            "hashed_password": hashed_password,
        }
        prev_data: UserDBRow = self.db[uid]
        new_data: UserDBRow = {**prev_data, **updated_data}
        self.db[uid] = new_data
        self.all_usernames.remove(prev_data["username"])
        self.all_usernames.add(new_data["username"])
        return UserOut.model_validate(new_data, extra="allow")

    async def pariatlly_update_user(
        self, uid: UUID4, partially_updated_user: UserOptionalIn
    ) -> UserOut:
        user_data = self.db[uid]
        prev_username = user_data["username"]
        for key, value in partially_updated_user.model_dump().items():
            if value is not None:
                user_data[key] = value  # type: ignore[]
        self.db[uid] = user_data
        new_username = user_data["username"]
        if new_username != prev_username:
            self.all_usernames.remove(prev_username)
            self.all_usernames.add(new_username)
        return UserOut.model_validate(user_data, extra="allow")

    async def delete_user(self, uid: UUID4) -> UserOut:
        deleted_user = self.db.pop(uid)
        self.all_usernames.remove(deleted_user["username"])
        return UserOut.model_validate(deleted_user, extra="allow")
