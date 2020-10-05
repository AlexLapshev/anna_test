from datetime import timedelta

from asyncpg import UniqueViolationError, StringDataRightTruncationError
from asyncpg.pool import Pool
from fastapi import Depends, status, HTTPException, APIRouter, Form
from fastapi.security import OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError
from loguru import logger
from starlette.responses import JSONResponse

from api.api_types import Token
from api.auth.auth import authenticate_user, hash_password
from api.auth.email_confirmation import send_email_confirm
from api.auth.jwt_work import create_access_token, decode_token
from api.database.database_connection import get_connection
from api.database.users_transactions import UserCRUD

token = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30


@token.post("/register")
async def register(username: str = Form(...), email: str = Form(...),
                   password: str = Form(...), password2: str = Form(...),
                   pool: Pool = Depends(get_connection)):
    if len(password) < 8:
        raise HTTPException(detail='password is too short', status_code=401)
    if password != password2:
        raise HTTPException(detail="passwords don't match", status_code=401)
    hashed_password = hash_password(password)
    try:
        await UserCRUD(pool).create_new_user(username, hashed_password, email)
        send_email_confirm(email)
        return JSONResponse(content={'result': 'succesfully register'}, status_code=201)
    except UniqueViolationError as e:
        raise HTTPException(detail='user with this username or email already exists', status_code=409)
    except StringDataRightTruncationError:
        raise HTTPException(detail="login or email are too long", status_code=401)


@token.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                pool: Pool = Depends(get_connection)) -> JSONResponse:
    if user := await authenticate_user(form_data.username, form_data.password, pool):
        logger.debug('authenticating user {}'.format(user.get('username')))
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.get('username')}, expires_delta=access_token_expires
        )
        return JSONResponse(content={"access_token": access_token,
                                     "token_type": "bearer", }, status_code=200)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@token.get("/confirm/{hash_email}")
async def confirm_user_email(hash_email: str, pool: Pool = Depends(get_connection)) -> JSONResponse:
    try:
        decoded = decode_token(hash_email)
        decoded_email = decoded.get('email')
    except ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"status": "expired token"})
    except JWTError:
        return JSONResponse(status_code=401, content={"status": "invalid token"})
    except ValueError as e:
        raise HTTPException(status_code=403, detail='invalid auth credentials')
    if user := await UserCRUD(pool).get_user_by_email(decoded_email):
        logger.debug(f'user is {user}')
        if user.get('confirmed'):
            return JSONResponse(status_code=403, content={"status": "user email is already confirmed"})
        await UserCRUD(pool).activate_user(user['user_id'])
        return JSONResponse(status_code=200, content={"result": "email successfully confirmed"})


