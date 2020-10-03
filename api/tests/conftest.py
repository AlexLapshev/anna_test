import asyncpg
import asyncio
import pytest

from fastapi.testclient import TestClient
from pathlib import Path


@pytest.fixture(scope="session")
def client():
    from api.main import app
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def access_token():
    from api.main import app
    with TestClient(app) as client:
        r = client.post(
            '/api/v1/users/token',
            data={'username': 'anna_test_user', 'password': 'password1'}
        )
        token = r.json().get('access_token')
        yield token


@pytest.fixture(scope="session", autouse=True)
def main():
    path_to_sql = Path(__file__).parent.absolute().joinpath('initdb.sql')
    sql_file = open(path_to_sql)
    connection = asyncio.get_event_loop().run_until_complete(asyncpg.connect(host='localhost', database='anna_test_db', user='anna_test_user', password='123456'))
    asyncio.get_event_loop().run_until_complete(connection.execute('''DROP SCHEMA public CASCADE; CREATE SCHEMA public;'''))
    asyncio.get_event_loop().run_until_complete(connection.execute(sql_file.read()))
    yield
    asyncio.get_event_loop().run_until_complete(connection.execute('''DROP SCHEMA public CASCADE; CREATE SCHEMA public;'''))
