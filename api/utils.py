import logging

from asyncpg.pool import Pool

from api.api_types import TaskChange
from api.database.tasks_transactions import TasksCRUD

logger = logging.getLogger(__name__)


async def check_updates(updates: TaskChange, pool: Pool, task_id: int):
    task = await TasksCRUD(pool).select_one_task(task_id)
    logger.debug('Время до обновления: {} .'.format(task.get('task_finish').strftime("%Y-%m-%d %H:%M")))
    logger.debug('Время для обновления: {} .'.format(updates.task_finish.strftime("%Y-%m-%d %H:%M")))
    if updates.task_finish.strftime("%Y-%m-%d %H:%M") != task.get('task_finish').strftime("%Y-%m-%d %H:%M"):
        print('Изменено время')
    print('Время не изменено')


class CheckUpdates:
    def __init__(self, updates: TaskChange, pool: Pool, task: dict):
        self.pool = pool
        self.updates = updates
        self.task = task

    async def check_name(self):
        if self.updates.task_name != self.task['task_name']:
            logger.debug('Название изменено')
        else:
            logger.debug('Название не изменено')

    async def check_date(self):
        if self.updates.task_finish.strftime("%Y-%m-%d %H:%M") != self.task.get('task_finish').strftime(
                "%Y-%m-%d %H:%M"):
            print('Изменено время')
        print('Время не изменено')

    async def check_description(self):
        if self.updates.task_name != self.task['task_name']:
            logger.debug('Описание изменено')
        else:
            logger.debug('Описание не изменено')
