import logging
from api.database.database_transactions import DatabaseTransactions

logger = logging.getLogger(__name__)


class UserCRUD:
    """Операции с пользователями"""
    def __init__(self, pool):
        self.pool = pool

    async def create_new_user(self, username: str, hashed_password: str):
        logger.info('creating new user: ', username)
        await DatabaseTransactions(self.pool).execute('''
        insert into users (username, hashed_password) values ('{}', '{}');
        ''', username, hashed_password)
