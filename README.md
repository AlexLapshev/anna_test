<h1>UserTasksApp using FastApi</h1>

<h2>Installation</h2>

_pip3 install -r requirements.txt_

<h2>Run</h2>

To run the app locally in **"debug-mode"** you should set environment variable _DEBUG=True_ and also 
to send email with confirm link you need to set _SENDER_EMAIL_ and _SENDER_PASSWORD_ environment variables.

Then you need to pull database image from dockerhub:
_docker pull alexlapshev/anna_test_db:1.0_.

And finally just _python -m api.main_.

To run the app in **"production-mode"** you need to set _SENDER_EMAIL_ and _SENDER_PASSWORD_ environment variables in docker-compose.yaml
and then just run _docker-compose up_ . 

<h2>Tests</h2>

To run tests you need to run docker image with database:
_docker run -p 5432:5432 alexlapshev/anna_test_db:1.0_ 

<h2>Requires</h2>
python => 3.8

_asyncpg_

_cryptography_

_fastapi_

_python-jose_

_passlib_

_pydantic_

_pytest_

_pytest-mock_

_uvicorn_