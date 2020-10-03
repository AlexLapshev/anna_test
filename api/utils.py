from asyncpg.pool import Pool
from fastapi import HTTPException
from loguru import logger

from api.api_types import TaskChange
from api.database.database_transactions import DatabaseTransactions
from api.database.tasks_transactions import TasksCRUD


class StatusCRUD:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def all_statuses(self):
        return await DatabaseTransactions(self.pool).select_multiple('''
        select status_name from status''')


class TaskValidation:
    """Валидация данных задач"""
    def __init__(self, pool: Pool = None):
        self.pool = pool

    async def get_task_params(self, status: str, order: str) -> None:
        logger.debug('validating params for get request')
        if order not in ['asc', 'desc']:
            raise HTTPException(detail='incorrect query parameter order', status_code=400)
        if status:
            statuses = await StatusCRUD(self.pool).all_statuses()
            status_names = [status['status_name'].lower() for status in statuses]
            if status.lower() not in status_names:
                raise HTTPException(detail='incorrect status name', status_code=400)

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
        if task['task_finish'].strftime("%Y-%m-%d %H:%M") != updates.task_finish:
            params_to_update['task_finish'] = updates.task_finish.strftime("%Y-%m-%d %H:%M")
        if task['task_name'] != updates.task_name:
            params_to_update['task_name'] = updates.task_name
        if task['task_description'] != updates.task_description:
            params_to_update['task_description'] = updates.task_description
        logger.debug(f'params to update: {params_to_update}')
        return params_to_update

