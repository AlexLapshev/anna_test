from datetime import timedelta

from asyncpg import UniqueViolationError
from asyncpg.pool import Pool
from fastapi import Depends, status, HTTPException, APIRouter, Form
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from starlette.responses import JSONResponse

from api.api_types import Token
from api.auth.auth import authenticate_user, hash_password
from api.auth.jwt_work import create_access_token
from api.database.database_connection import get_connection
from api.database.users_transactions import UserCRUD

token = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30


@token.post("/register")
async def register(username: str = Form(...), password: str = Form(...), password2: str = Form(...),
                   pool: Pool = Depends(get_connection)):
    if len(password) < 8:
        return JSONResponse(content={'detail': 'password is too short'}, status_code=401)
    if password != password2:
        return JSONResponse(content={'detail': "passwords don't match"}, status_code=401)
    hashed_password = hash_password(password)
    try:
        await UserCRUD(pool).create_new_user(username, hashed_password)
        return JSONResponse(content={'result': 'succesfully register'}, status_code=201)
    except UniqueViolationError as e:
        return JSONResponse(content={'detail': 'user with this username already exist'}, status_code=409)


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
