from api.database.database_transactions import DatabaseTransactions
from loguru import logger


class UserCRUD:
    """Операции с пользователями"""
    def __init__(self, pool):
        self.pool = pool

    async def create_new_user(self, username: str, hashed_password: str, email: str):
        logger.info('creating new user: ', username)
        await DatabaseTransactions(self.pool).execute('''
        insert into users (username, hashed_password, user_email, confirmed) values ('{}', '{}', '{}', false);
        ''', username, hashed_password, email)

    async def get_user_by_email(self, email) -> dict:
        logger.debug(f'getting user with email: {email}')
        return await DatabaseTransactions(self.pool).select('''
        select * from users where user_email = '{}';
        ''', email)

    async def activate_user(self, user_id: int):
        logger.info(f'updating user email_confirmation, user_id: {user_id}')
        await DatabaseTransactions(self.pool).execute('''
        update users set confirmed = true where user_id = {}
        ''', user_id)
