import asyncio
import asyncpg
import pytest

from urllib.parse import quote

test_url = "/api/v1/tasks"


@pytest.mark.parametrize('date, status, order, status_code', [
    ('2020-10-03', 'новая', 'desc', 200),
    ('2020-10-03', 'новая', 'asc', 200),
    ('2020-10-03', 'ошибочная', 'desc', 400),
    ('2020-10-03', 'новая', 'fail', 400),
],
                         )
def test_user_tasks(client, access_token, date, status, order, status_code):
    query = f'?date={date}&status={quote(status)}&order={order}'
    response = client.get(
        test_url + query,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


@pytest.mark.parametrize('status, order, status_code', [
    ('новая', 'desc', 200),
    ('новая', 'asc', 200),
    ('ошибочная', 'desc', 400),
    ('новая', 'fail', 400),
],
                         )
def test_user_tasks_without_date(client, access_token, status, order, status_code):
    query = f'?status={quote(status)}&order={order}'
    response = client.get(
        test_url + query,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


@pytest.mark.parametrize('date, status, status_code', [
    ('2020-10-03', 'новая', 200),
    ('2020-10-03', 'ошибочная', 400),
],
                         )
def test_user_tasks_without_order(client, access_token, date, status, status_code):
    query = f'?status={quote(status)}&date={date}'
    response = client.get(
        test_url + query,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


@pytest.mark.parametrize('task_name, task_description, task_finish, status_code', [
    ("задача в тестах", "описание", "2020-10-01 00:00", 201),
    ("задача в тестах2", "description", None, 201),
    ("", "описание", "2020-10-01 00:00", 400),
    (None, "описание", "2020-10-01 00:00", 422),
    ("a" * 30, "описание", "2020-10-01 00:00", 400),
    ("задача в тестах2", "", "2020-10-01 00:00", 400),
    ("задача в тестах2", None, "2020-10-01 00:00", 422),
    ("задача в тестах2", "a" * 256, "2020-10-01 00:00", 400),
    ("задача в тестах", "описание", "2020-10-01 00:00", 409),
])
def test_create_task(client, access_token, task_name, task_description, task_finish, status_code):
    response = client.post(
        test_url,
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            "task_name": task_name,
            "task_description": task_description,
            "task_finish": task_finish
        }
    )
    assert response.status_code == status_code


def test_no_tasks(client, access_token):
    connection = asyncio.get_event_loop().run_until_complete(
        asyncpg.connect(host='localhost', database='anna_test_db', user='anna_test_user', password='123456'))
    asyncio.get_event_loop().run_until_complete(connection.execute('''delete from tasks where user_id = 1'''))
    response = client.get(
        test_url,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 204


@pytest.mark.parametrize('task_name, task_description, task_finish, status_code', [
    ("задача в тестах", "описание", "2020-10-01 00:00", 201),
    ("задача в тестах2", "описание", None, 201),
    ("задача в тестах", "описание", "2020-10-01 00:00", 409),
    (None, "описание", "2020-10-01 00:00", 422),
    ("", "описание", "2020-10-01 00:00", 400),
    ("a" * 30, "описание", "2020-10-01 00:00", 400),
    ("задача в тестах2", "", "2020-10-01 00:00", 400),
    ("задача в тестах2", None, "", 422),
    ("задача в тестах2", "a"*256, "2020-10-01 00:00", 400),
])
def test_update_task(client, access_token, task_name, task_description, task_finish, status_code):
    response = client.post(
        test_url,
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            "task_name": task_name,
            "task_description": task_description,
            "task_finish": task_finish
        }
    )
    assert response.status_code == status_code