from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from psycopg_pool import AsyncConnectionPool

import untitled_python_project_1.users.service as us
from untitled_python_project_1.dependencies import get_global_settings
from untitled_python_project_1.users import router as users_router
from untitled_python_project_1.users.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None]:
    async with AsyncConnectionPool(
        conninfo=get_global_settings().get_db_url, min_size=2, max_size=10, open=False
    ) as apool:
        async with apool.connection() as aconn:
            users_exist = await us.create_users(aconn)
            if not users_exist:
                raise RuntimeError("users database does not exist and could not be created")
        fastapi_app.state.apool = apool
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router.router)


@app.exception_handler(UserNotFoundError)
async def user_not_found_error_handler(_: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": f"User with uid {exc.uid} not found in the user database."},
    )


@app.exception_handler(UsernameAlreadyExistsError)
async def username_already_exists_error(
    _: Request, exc: UsernameAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": f"User with username {exc.username} already exists"},
    )


@app.exception_handler(EmailAlreadyExistsError)
async def email_already_exists_error(_: Request, exc: EmailAlreadyExistsError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": f"User with email {exc.email} already exists"},
    )


@app.get("/")
async def root() -> dict[str, Any]:
    return {"Bello": "Papaya"}
