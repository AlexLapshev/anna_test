from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import Request


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.pool


async def get_connection(pool: Pool = Depends(_get_db_pool)):
    return pool
