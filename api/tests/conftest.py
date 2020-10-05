import asyncpg
import asyncio
import pytest

from loguru import logger

from fastapi.testclient import TestClient

TEST_USERS = '''
    insert into users (username, hashed_password, user_email, confirmed)
    values 
    ('anna_test_user', '$6$rounds=656000$qd6ejNiPCAHXLQ0q$3/kUqu/Xuili5leabQFKCO3Q9wf3fmgcyGxjz/KppBc.79t9lM2mXrzA5h9qspCqYCBy/d4M3cJ1j6MP/Drg91', 'test@m.ru', true);
'''

TEST_TASKS = '''
    insert into tasks (task_name, task_description, task_created, task_finish, task_status, user_id)
    values 
    ('Сделать тестовое', 'Тестовое на fastapi', '2020-09-30 21:00', '2020-10-03 21:00','новая', 1),
    ('Сделать тестовое2', 'Тестовое на fastapi', '2020-09-30 21:00', '2020-10-03 21:00','в работе', 1);
'''

TEST_AUDIT = '''
    insert into tasks_audit (task_id, user_id, task_operation, prev_value, date_change)
    values 
    (1, 1, 'task_name', 'в работе', '2020-10-03 16:01:27');
'''


async def execute_sql(sql):
    conn = await asyncpg.connect(host='localhost', database='anna_test_db', user='anna_test_user', password='123456')
    await conn.execute(sql)
    await conn.close()


@pytest.fixture(scope="session")
def client():
    from api.main import app
    with TestClient(app) as client:
        yield client
        asyncio.get_event_loop().run_until_complete(execute_sql('''
        alter sequence tasks_audit_audit_id_seq restart with 1;
        alter sequence tasks_task_id_seq restart with 1;
        '''))


@pytest.fixture(scope='session')
def access_token():
    logger.debug('creating test access token')
    from api.main import app
    with TestClient(app) as client:
        r = client.post(
            '/api/v1/users/token',
            data={'username': 'anna_test_user', 'password': 'password1'}
        )
        token = r.json().get('access_token')
        logger.debug(f'creating test access token {token}')
        yield token


@pytest.fixture(scope='session', autouse=True)
def user():
    asyncio.get_event_loop().run_until_complete(execute_sql(TEST_USERS))
    yield
    asyncio.get_event_loop().run_until_complete(execute_sql('truncate users cascade;'))
    asyncio.get_event_loop().run_until_complete(execute_sql('alter sequence users_user_id_seq restart with 1;'))


@pytest.fixture
def tasks():
    asyncio.get_event_loop().run_until_complete(execute_sql(TEST_TASKS))
    yield
    asyncio.get_event_loop().run_until_complete(execute_sql('truncate tasks cascade'))
    asyncio.get_event_loop().run_until_complete(execute_sql('alter sequence tasks_task_id_seq restart with 1;'))


@pytest.fixture
def tasks_audit():
    asyncio.get_event_loop().run_until_complete(execute_sql(TEST_AUDIT))
    yield
    asyncio.get_event_loop().run_until_complete(execute_sql('truncate tasks_audit cascade'))
    asyncio.get_event_loop().run_until_complete(execute_sql('alter sequence tasks_audit_audit_id_seq restart with 1;'))


