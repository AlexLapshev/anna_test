from datetime import date
from typing import List

from asyncpg.pool import Pool
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette.responses import JSONResponse

from api.api_types import Task, BaseTask, TaskChange
from api.auth.auth import get_current_user
from api.database.database_connection import get_connection
from api.database.tasks_transactions import TasksCRUD
from api.utils import TaskValidation

tasks = APIRouter()


@tasks.get('', response_model=List[Task])
async def user_tasks(date: date = None, status: str = None, order: str = 'desc', pool: Pool = Depends(get_connection),
                     current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    await TaskValidation(pool).get_task_params(status, order)
    if status or date:
        user_t = await TasksCRUD(pool).select_tasks_with_queries(status, date, order, user_id)
    else:
        user_t = await TasksCRUD(pool).select_all_tasks(order, user_id)
    if user_t:
        return user_t
    else:
        return JSONResponse(content={'detail': 'user has no tasks'}, status_code=204)


@tasks.post('')
async def create_task(task: BaseTask, pool: Pool = Depends(get_connection),
                      current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    await TasksCRUD(pool).create_task(user_id, task)
    return JSONResponse(content={'result': 'task created'}, status_code=201)


@tasks.put('/{task_id}/change')
async def change_task(task_id: int, updates: TaskChange, pool: Pool = Depends(get_connection),
                      current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    if task := await TasksCRUD(pool).select_one_task_by_id(task_id, user_id):
        updates = TaskValidation().task_update_params(task, updates)
        await TasksCRUD(pool).update_task(task_id, updates)
        await TasksCRUD(pool).update_audit(task_id, user_id, updates)
    else:
        raise HTTPException(detail="task doesn't belong to user", status_code=403)
    return JSONResponse(content={'result': 'task updated'}, status_code=201)
