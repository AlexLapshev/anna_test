import asyncpg
import logging.config
import uvicorn


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from api.tasks import tasks

logging.config.fileConfig(Path.joinpath(Path(__file__).parent, 'logging.conf'), disable_existing_loggers=False)


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
    app.router.add_event_handler("startup", create_startup_hook(app))
    return app


def create_startup_hook(app: FastAPI):
    async def startup_hook() -> None:
        app.state.pool = await asyncpg.create_pool(dsn="postgres://anna_test_user:123456@0.0.0.0:5432/anna_test_db")
    return startup_hook


app = create_app()


if __name__ == "__main__":
    uvicorn.run('api.main:app', host="0.0.0.0", port=1984, reload=True, workers=4)