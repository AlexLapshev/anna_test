from datetime import date
from typing import List

from asyncpg import UniqueViolationError
from asyncpg.pool import Pool
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from api.database.database_connection import get_connection
from api.database.tasks_transactions import TasksCRUD
from api.api_types import Task, BaseTask, TaskChange
from api.utils import check_updates, CheckUpdates

tasks = APIRouter()


@tasks.get('/', response_model=List[Task])
async def user_tasks(date: date = None, status: str = None, order: str = 'desc', pool: Pool = Depends(get_connection)):
    if order not in ['asc', 'desc']:
        return JSONResponse(content={'error': 'incorrect query parameter order'})
    if status or date:
        return await TasksCRUD(pool).select_task_with_queries(status, date, order)
    return await TasksCRUD(pool).select_all_tasks(order)


@tasks.post('/create')
async def create_task(task: BaseTask, pool: Pool = Depends(get_connection)):
    try:
        await TasksCRUD(pool).create_task(task.task_name, task.task_description, task.task_finish)
    except UniqueViolationError:
        return JSONResponse(content='not unique task name', status_code=409)
    return JSONResponse(content='task created', status_code=201)


@tasks.post('/{task_id}/change')
async def change_task(task_id: int, updates: TaskChange, pool: Pool = Depends(get_connection)):
    await TasksCRUD(pool).update_task(task_id, updates)
    return JSONResponse(content='task updated', status_code=201)

    # await check_updates(updates, pool, task_id)
    # task = await TasksCRUD(pool).select_one_task(task_id)
    # await CheckUpdates(updates, pool, task).check_date()
    # try:
    #     await TasksCRUD(pool).update_task(task.task_name, task.task_description)
    # except UniqueViolationError:
    #     return JSONResponse(content='not unique task name', status_code=409)
    # return JSONResponse(content='task created', status_code=201)
    pass

