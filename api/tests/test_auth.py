import pytest

test_url = "/api/v1/users"


@pytest.mark.parametrize('username, password, password2, email, status_code', [
    ('test', '1', '1', 'test@gmail.ru', 401),
    ('test', '123456789', '1234567890', 'test@gmail.ru', 401),
    ('test', '123456789', '123456789', 'test@gmail.ru', 201),
    ('anna_test_user', '123456789', '123456789', 'test@gmail.ru', 409),
    ('test', '123456789', '123456789', 'test@m.ru', 409),
])
def test_registration(client, mocker, username, password, password2, email, status_code):
    mocker.patch('api.auth.token.send_email_confirm', return_value=None)
    response = client.post(
        test_url + '/register',
        data={
            'username': username,
            'password': password,
            'password2': password2,
            'email': email
        }
    )
    assert response.status_code == status_code


@pytest.mark.parametrize('username, password, status_code', [
    ('anna_test_user', 'password1', 200),
    ('anna_test_use', 'password1', 401),
    ('anna_test_user', '123456789', 401),
])
def test_login(client, username, password, status_code):
    response = client.post(
        test_url + '/token',
        data={
            'username': username,
            'password': password,
        }
    )
    assert response.status_code == status_code
