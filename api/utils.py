from typing import Optional

from asyncpg.pool import Pool
from datetime import date
from fastapi import HTTPException
from loguru import logger

from api.api_types import TaskChange, STATUSES
from api.database.database_transactions import DatabaseTransactions
from api.database.tasks_transactions import TasksCRUD

ORDER = ['asc', 'desc']
CHANGE_OPERATIONS = ['task_status', 'task_finish', 'task_name', 'task_description']


class StatusCRUD:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def all_statuses(self):
        return await DatabaseTransactions(self.pool).select_multiple('''
        select status_name from ''')


class TaskValidation:
    """Валидация данных задач"""
    def __init__(self, pool: Pool = None):
        self.pool = pool

    async def user_task_belonging(self, task_id: int, user_id: int):
        user_task_ids = [task['task_id'] for task in await TasksCRUD(self.pool).select_all_tasks('desc', user_id)]
        if task_id in user_task_ids:
            pass
        else:
            raise HTTPException(detail="task doesn't belong to user", status_code=403)

    @staticmethod
    def task_update_params(task: dict, updates: TaskChange) -> dict:
        params_to_update = {}
        if task['task_status'] != updates.task_status:
            params_to_update['task_status'] = updates.task_status
        if task['task_finish'].strftime("%Y-%m-%d %H:%M") != updates.task_finish.strftime("%Y-%m-%d %H:%M"):
            params_to_update['task_finish'] = updates.task_finish.strftime("%Y-%m-%d %H:%M")
        if task['task_name'] != updates.task_name:
            params_to_update['task_name'] = updates.task_name
        if task['task_description'] != updates.task_description:
            params_to_update['task_description'] = updates.task_description
        logger.debug(f'params to update: {params_to_update}')
        return params_to_update


async def common_parameters(date: Optional[date] = None, status: Optional[str] = None,
                            order: Optional[str] = 'desc') -> dict:
    logger.debug('validating params for get request')
    if order not in ORDER:
        raise HTTPException(detail='incorrect query parameter order', status_code=400)
    if status:
        status = status.lower()
        if status not in STATUSES:
            raise HTTPException(detail='incorrect query parameter status', status_code=400)
    return {"date": date, "status": status, "order": order}


async def change_parameters(task_operation: Optional[str] = None) -> dict or None:
    logger.debug('validating change parameter')
    if task_operation:
        task_operation = task_operation.lower()
        if task_operation not in CHANGE_OPERATIONS:
            raise HTTPException(detail='incorrect query parameter task_operation', status_code=400)
        return task_operation
