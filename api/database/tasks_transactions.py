from loguru import logger

from asyncpg.pool import Pool
from datetime import datetime
from fastapi import HTTPException


from api.api_types import TaskChange, BaseTask
from api.database.database_transactions import DatabaseTransactions


class TasksCRUD:
    """Операции над задачами"""

    def __init__(self, pool: Pool):
        self.pool = pool

    async def select_one_task_by_id(self, task_id: int, user_id) -> dict:
        logger.debug(f'selecting task with name: {task_id}')
        return await DatabaseTransactions(self.pool).select('''
        select * from tasks where task_id='{}' and user_id = {};
        ''', task_id, user_id)

    async def select_one_task_by_name(self, task_name: str, user_id: int) -> dict:
        logger.debug(f'selecting task with name: {task_name}')
        return await DatabaseTransactions(self.pool).select('''
        select * from tasks where task_name='{}' and user_id = {};
        ''', task_name, user_id)

    async def select_all_tasks(self, order: str, user_id: int) -> list:
        logger.debug('selecting all task')
        return await DatabaseTransactions(self.pool).select_multiple('''
        select task_name, task_description, task_finish, task_id, task_created, user_id, task_status
            from tasks
            where user_id = {} 
            order by task_created {};
        ''', user_id, order)

    async def select_tasks_with_queries(self, status: str, date: datetime, order: str, user_id: int) -> list:
        logger.debug('user_id: ', user_id)
        main_query = '''
            select task_name, task_description, task_finish, task_id, task_created, user_id, task_status
            from tasks
            where user_id = {} and 
            '''
        if date and status:
            logger.debug('selecting tasks filtered by date and status')
            return await DatabaseTransactions(self.pool).select_multiple(main_query + '''
            date(task_finish) = '{}' and task_status = '{}'
            order by task_finish {};
            ''', user_id, date, status.lower(), order)
        elif status:
            logger.debug('selecting tasks filtered by status')
            return await DatabaseTransactions(self.pool).select_multiple(main_query + '''
            task_status = '{}'
            order by task_finish {};
            ''', user_id, status.lower(), order)
        else:
            logger.debug('selecting tasks filtered by date')
            return await DatabaseTransactions(self.pool).select_multiple(main_query + '''
            date(task_finish) = '{}'
            order by task_finish {};
            ''', user_id, date, order)

    async def create_task(self, user_id: int, task: BaseTask) -> None:
        base_query = "insert into tasks (task_name, task_description, task_created, task_finish, task_status, user_id) "
        logger.debug(f'creating task with name: {task.task_name}')
        if await self.select_one_task_by_name(task.task_name, user_id):
            raise HTTPException(status_code=409, detail='user already has task with this name')
        task_created = datetime.now().strftime("%Y-%m-%d %H:%M")
        if task.task_finish:
            logger.debug(f'formatting date {task.task_finish}')
            task_finish = task.task_finish.strftime("%Y-%m-%d %H:%M")
            quotes = "values ('{}', '{}', '{}', '{}', '{}', {});"
        else:
            task_finish = 'null'
            quotes = "values ('{}', '{}', '{}', {}, '{}', {});"
        logger.debug(base_query + quotes)
        await DatabaseTransactions(self.pool).execute(base_query + quotes, task.task_name,
                                                      task.task_description, task_created,
                                                      task_finish, 'новая', user_id)

    async def update_task(self, task_id: int, updates: dict):
        logger.info('updating task')
        logger.debug(updates)
        base_query = 'update tasks set '
        for k, v in updates.items():
            if type(v) == str:
                string = k + " = '{}',"
            else:
                string = k + ' = {},'
            if not v:
                updates[k] = 'null'
            base_query += string
        base_query = base_query[:-1]
        base_query += " where task_id={};"
        await DatabaseTransactions(self.pool).execute(base_query, *updates.values(), task_id)

    async def update_audit(self, task_id: int, user_id: int, updates: dict):
        logger.debug(f'update params: {updates}')
        for k, v in updates.items():
            date_change = datetime.now().strftime("%Y-%m-%d %H:%M")
            await DatabaseTransactions(self.pool).execute('''
            insert into tasks_audit (task_id, user_id, date_change, task_operation, prev_value) 
            values ({}, {}, '{}', '{}', '{}');
            ''', task_id, user_id, date_change, k, str(v))

    async def task_changes(self, task_id):
        return await DatabaseTransactions(self.pool).select_multiple('''
        select * from tasks_audit where task_id = {};
        ''', task_id)

    async def task_changes_with_query(self, task_id: int, operation: str):
        logger.debug(f'filtering with query {operation}')
        return await DatabaseTransactions(self.pool).select_multiple('''
        select * from tasks_audit where task_id = {} and task_operation = '{}';
        ''', task_id, operation)
