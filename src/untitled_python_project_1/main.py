from fastapi import FastAPI

from untitled_python_project_1.users import router as users_router

app = FastAPI()

app.include_router(users_router.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"Bello": "Papaya"}
