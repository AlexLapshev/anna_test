import pytest

from urllib.parse import quote

test_url = "/api/v1/tasks"


@pytest.mark.usefixtures('tasks')
@pytest.mark.parametrize('date, status, order, status_code', [
    ('2020-10-03', 'новая', 'desc', 200),
    ('2020-10-03', 'новая', 'asc', 200),
    ('2020-10-03', 'ошибочная', 'desc', 400),
    ('2020-10-03', 'новая', 'fail', 400),
])
def test_user_tasks(client, access_token, date, status, order, status_code):
    query = f'?date={date}&status={quote(status)}&order={order}'
    response = client.get(
        test_url + query,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


@pytest.mark.usefixtures('tasks')
@pytest.mark.parametrize('status, order, status_code', [
    ('новая', 'desc', 200),
    ('В работе', 'asc', 200),
    ('ошибочная', 'desc', 400),
    ('новая', 'fail', 400),
])
def test_user_tasks_without_date(client, access_token, status, order, status_code):
    query = f'?status={quote(status)}&order={order}'
    response = client.get(
        test_url + query,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


@pytest.mark.usefixtures('tasks')
@pytest.mark.parametrize('date, status, status_code', [
    ('2020-10-03', 'новая', 200),
    ('2020-10-03', 'ошибочная', 400),
])
def test_user_tasks_without_order(client, access_token, date, status, status_code):
    query = f'?status={quote(status)}&date={date}'
    response = client.get(
        test_url + query,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


@pytest.mark.usefixtures('tasks', 'tasks_audit')
@pytest.mark.parametrize('task_name, task_description, task_finish, status_code', [
    ("задача в тестах", "описание", "2020-10-01 00:00", 201),
    ("задача в тестах2", "description", None, 201),
    ("", "описание", "2020-10-01 00:00", 400),
    (None, "описание", "2020-10-01 00:00", 422),
    ("a" * 30, "описание", "2020-10-01 00:00", 400),
    ("задача в тестах2", "", "2020-10-01 00:00", 400),
    ("задача в тестах2", None, "2020-10-01 00:00", 422),
    ("задача в тестах2", "a" * 256, "2020-10-01 00:00", 400),
    ("Сделать тестовое", "описание", "2020-10-01 00:00", 409),
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


@pytest.mark.usefixtures('tasks', 'tasks_audit')
@pytest.mark.parametrize('task_id, task_name, task_description, task_finish, task_status, status_code', [
    (1, 'Сделать тестовое', 'Тестовое на fastapi', '2020-10-03 21:00', 'новая', 204),
    (1, "новая задача в тестах", "описание", "2020-10-01 00:00", "новая", 201),
    (1, "задача в тестах2", "описание", None, "новая", 201),
    (1, None, "описание", "2020-10-01 00:00", "новая", 422),
    (1, "", "описание", "2020-10-01 00:00", "новая", 400),
    (1, "a" * 30, "описание", "2020-10-01 00:00", "новая", 400),
    (1, "задача в тестах2", "", "2020-10-01 00:00", "новая", 400),
    (1, "задача в тестах2", None, "", "новая", 422),
    (1, "задача в тестах2", "a"*256, "2020-10-01 00:00", "новая", 400),
])
def test_update_task(client, access_token, task_id, task_name, task_description, task_finish, task_status, status_code):
    response = client.put(
        test_url + f'/{task_id}',
        headers={'Authorization': 'Bearer ' + access_token},
        json={
            "task_name": task_name,
            "task_description": task_description,
            "task_finish": task_finish,
            "task_status": task_status
        }
    )
    assert response.status_code == status_code


@pytest.mark.usefixtures('tasks', 'tasks_audit')
@pytest.mark.parametrize('task_id, status_code', [
    (1, 200),
])
def test_task_changes(client, access_token, task_id, status_code):
    response = client.get(
        test_url + f'/{task_id}/changes',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


@pytest.mark.usefixtures('tasks', 'tasks_audit')
@pytest.mark.parametrize('task_id, operation, status_code', [
    (1, 'task_name', 200),
    (1, 'task_status', 204),
    (1, 'task_name', 200),
    (1, 'failed', 400),
    (22, 'task_name', 403),
])
def test_task_changes_with_queries(client, access_token, task_id, operation, status_code):
    response = client.get(
        test_url + f'/{task_id}/changes' + f'?task_operation={operation}',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == status_code


def test_no_tasks(client, access_token):
    response = client.get(
        test_url,
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.status_code == 204
