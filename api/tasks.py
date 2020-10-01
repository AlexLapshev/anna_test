from datetime import date
from typing import List

from asyncpg import StringDataRightTruncationError
from asyncpg.pool import Pool
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from api.auth.auth import get_current_user
from api.database.database_connection import get_connection
from api.database.database_transactions import DatabaseTransactions
from api.database.tasks_transactions import TasksCRUD, StatusCRUD
from api.api_types import Task, BaseTask, TaskChange

tasks = APIRouter()


@tasks.get('', response_model=List[Task])
async def user_tasks(date: date = None, status: str = None, order: str = 'desc', pool: Pool = Depends(get_connection),
                     current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    if order not in ['asc', 'desc']:
        return JSONResponse(content={'error': 'incorrect query parameter order'}, status_code=400)
    status_names = await StatusCRUD(pool).all_statuses()
    status_names = [status['status_name'].lower() for status in status_names]
    if status.lower() not in status_names:
        return JSONResponse(content={'error': 'incorrect status name'}, status_code=400)
    if status or date:
        return await TasksCRUD(pool).select_tasks_with_queries(status, date, order, user_id)
    return await TasksCRUD(pool).select_all_tasks(order, user_id)


@tasks.post('')
async def create_task(task: BaseTask, pool: Pool = Depends(get_connection),
                      current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    if len(task.task_name) > 25:
        return JSONResponse(content={'error': 'task name is too long'}, status_code=400)
    if len(task.task_name) < 1:
        return JSONResponse(content={'error': 'task name is too short'}, status_code=400)
    if len(task.task_description) > 255:
        return JSONResponse(content={'error': 'task description is too long'}, status_code=400)
    try:
        await TasksCRUD(pool).create_task(task.task_name, task.task_description, task.task_finish, user_id)
    except ValueError as e:
        return JSONResponse(content=str(e), status_code=409)
    return JSONResponse(content='task created', status_code=201)


@tasks.put('/{task_id}/change')
async def change_task(task_id: int, updates: TaskChange, pool: Pool = Depends(get_connection),
                      current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    statuses = await StatusCRUD(pool).all_statuses()
    status_names = [status['status_name'] for status in statuses]
    if updates.task_status not in status_names:
        return JSONResponse(content={'error': 'incorrect status'}, status_code=422)
    try:
        await TasksCRUD(pool).update_task(task_id, updates, user_id)
        return JSONResponse(content='task updated', status_code=201)
    except ValueError as e:
        return JSONResponse(content={'error': str(e)}, status_code=409)
    except StringDataRightTruncationError as e:
        return JSONResponse(content={'error': 'task_name or description is too long'}, status_code=409)
