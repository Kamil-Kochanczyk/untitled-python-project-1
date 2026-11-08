from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from untitled_python_project_1.users import router as users_router
from untitled_python_project_1.users.exceptions import (
    UsernameAlreadyExistsError,
    UserNotFoundError,
)

app = FastAPI()


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


@app.get("/")
async def root() -> dict[str, str]:
    return {"Bello": "Papaya"}
