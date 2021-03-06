import asyncpg
import os
import uvicorn


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth.token import token
from api.tasks import tasks


if os.getenv('DEBUG') == 'True':
    reload = True
    postgres_url = "postgres://anna_test_user:123456@0.0.0.0:5432/anna_test_db"
else:
    reload = False
    postgres_url = "postgres://anna_test_user:123456@db:5432/anna_test_db"


def create_app():
    app = FastAPI(debug=True)
    origins = [
        "http://0.0.0.0:8080",
        "http://localhost:8080",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(tasks, prefix='/api/v1/tasks', tags=['tasks'])
    app.include_router(token, prefix='/api/v1/users', tags=['token'])
    app.router.add_event_handler("startup", create_startup_hook(app))
    return app


def create_startup_hook(app: FastAPI):
    async def startup_hook() -> None:
        app.state.pool = await asyncpg.create_pool(dsn=postgres_url)
    return startup_hook


app = create_app()


if __name__ == "__main__":
    uvicorn.run('api.main:app', host="0.0.0.0", port=1984, reload=reload, workers=4)
