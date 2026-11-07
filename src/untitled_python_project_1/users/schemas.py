import datetime as dt
from typing import Annotated, Any, TypedDict

from pydantic import UUID4, BaseModel, EmailStr, Field, SecretStr, field_serializer

import untitled_python_project_1.users.constants as uc


class UserBase(BaseModel):
    first_name: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_FIRST_NAME,
            pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
        ),
    ]
    surname: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_SURNAME,
            pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
        ),
    ]
    username: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_USERNAME,
            pattern=r"^[A-Za-z0-9-_]+$",
        ),
    ]
    email: EmailStr


class UserIn(UserBase):
    password: SecretStr


class UserOut(UserBase):
    uuid4: UUID4
    is_active: bool
    created_at: dt.datetime
    modified_at: dt.datetime

    @field_serializer("created_at", "modified_at", mode="plain", when_used="json")
    def isoformat_timestamps(self, value: Any) -> Any:
        if isinstance(value, dt.datetime):
            return value.strftime("%d-%m-%Y, %H:%M:%S")
        return value


class UserProvidedData(TypedDict):
    first_name: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_FIRST_NAME,
            pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
        ),
    ]
    surname: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_SURNAME,
            pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
        ),
    ]
    username: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_USERNAME,
            pattern=r"^[A-Za-z0-9-_]+$",
        ),
    ]
    email: EmailStr
    hashed_password: str


class UserGeneratedData(TypedDict):
    uuid4: UUID4
    is_active: bool
    created_at: dt.datetime
    modified_at: dt.datetime


class UserDBRow(TypedDict):
    uuid4: UUID4
    first_name: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_FIRST_NAME,
            pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
        ),
    ]
    surname: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_SURNAME,
            pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
        ),
    ]
    username: Annotated[
        str,
        Field(
            min_length=uc.MIN_LEN,
            max_length=uc.MAX_LEN_USERNAME,
            pattern=r"^[A-Za-z0-9-_]+$",
        ),
    ]
    email: EmailStr
    hashed_password: str
    is_active: bool
    created_at: dt.datetime
    modified_at: dt.datetime


class UserOptionalBase(BaseModel):
    first_name: (
        Annotated[
            str,
            Field(
                min_length=uc.MIN_LEN,
                max_length=uc.MAX_LEN_FIRST_NAME,
                pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
            ),
        ]
        | None
    ) = None
    surname: (
        Annotated[
            str,
            Field(
                min_length=uc.MIN_LEN,
                max_length=uc.MAX_LEN_SURNAME,
                pattern=r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž\s'-]+$",
            ),
        ]
        | None
    ) = None
    username: (
        Annotated[
            str,
            Field(
                min_length=uc.MIN_LEN,
                max_length=uc.MAX_LEN_USERNAME,
                pattern=r"^[A-Za-z0-9-_]+$",
            ),
        ]
        | None
    ) = None
    email: EmailStr | None = None


class UserOptionalIn(UserOptionalBase):
    password: SecretStr | None = None
