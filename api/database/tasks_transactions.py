import logging

from datetime import datetime
from asyncpg.pool import Pool

from api.api_types import TaskChange
from api.database.database_transactions import DatabaseTransactions

logger = logging.getLogger(__name__)


class TasksCRUD:
    """Операции над задачами"""

    def __init__(self, pool: Pool):
        self.pool = pool

    async def select_one_task(self, task_id: int) -> dict:
        logger.info(f'selecting task with id: {task_id}')
        return await DatabaseTransactions(self.pool).select('''select * from tasks where task_id={};''', task_id)

    async def select_all_tasks(self, order: str, user_id: int) -> list:
        logger.info('selecting all task')
        return await DatabaseTransactions(self.pool).select_multiple('''
        select * from tasks where user_id = {} order by task_created {};
        ''', user_id, order)

    async def select_tasks_with_queries(self, status: str, date: datetime, order: str, user_id: int) -> list:
        logger.debug('user_id: ', user_id)
        main_query = '''
            select task_name, task_description, task_finish, task_id, task_created, user_id, status_name as task_status
            from tasks
            join status ON tasks.task_status=status.status_id
            where user_id = {} and 
            '''
        if date and status:
            logger.info('selecting tasks filtered by date and status')
            return await DatabaseTransactions(self.pool).select_multiple(main_query + '''
            date(task_finish) = '{}' and lower(status.status_name) = lower('{}')
            order by task_finish {};
            ''', user_id, date, status, order)
        elif status:
            logger.info('selecting tasks filtered by status')
            return await DatabaseTransactions(self.pool).select_multiple(main_query + '''
            lower(status.status_name) = lower('{}')
            order by task_finish {};
            ''', user_id, status, order)
        else:
            logger.info('selecting tasks filtered by date')
            return await DatabaseTransactions(self.pool).select_multiple(main_query + '''
            date(task_finish) = '{}'
            order by task_finish {};
            ''', user_id, date, order)

    async def create_task(self, task_name: str, task_description: str, task_finish: datetime, user_id: int) -> None:
        logger.info(f'creating task with name: {task_name}')
        task_created = datetime.now().strftime("%Y-%m-%d %H:%M")
        if await DatabaseTransactions(self.pool).select('''
        select * from tasks 
        where user_id={} and task_name='{}';
        ''', user_id, task_name):
            raise ValueError('user already has task with this name')
        await DatabaseTransactions(self.pool).execute('''
        insert into tasks (task_name, task_description, task_created, task_finish, task_status, user_id) 
        values ('{}', '{}', '{}', '{}', {}, {});''', task_name, task_description, task_created,
                                                      task_finish.strftime("%Y-%m-%d %H:%M"), 1, user_id)

    async def update_task(self, task_id: int, updates: TaskChange, user_id: int):
        logger.info('updating task')
        user_task_ids = [task['task_id'] for task in await self.select_all_tasks('desc', user_id)]
        print(user_task_ids)
        if task_id in user_task_ids:
            await DatabaseTransactions(self.pool).execute('''
            update tasks 
            set task_status = {}, task_name = '{}', task_description = '{}', task_finish = '{}' 
            where task_id={};
            ''', updates.task_status, updates.task_name, updates.task_description, updates.task_finish, task_id)
        else:
            raise ValueError('foreign task')
