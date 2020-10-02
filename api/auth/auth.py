from asyncpg.pool import Pool
from jose import JWTError, ExpiredSignatureError
from passlib.context import CryptContext


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from api.auth.jwt_work import decode_token
from api.api_types import TokenData
from api.database.database_transactions import DatabaseTransactions
from api.database.database_connection import get_connection

pwd_context = CryptContext(schemes=["sha512_crypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str, pool: Pool) -> dict or bool:
    user = await DatabaseTransactions(pool).select('''SELECT * FROM users WHERE username = '{}' ''', username)
    if not user:
        return False
    if not verify_password(password, user.get('hashed_password')):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), pool: Pool = Depends(get_connection)) -> dict:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Expired token", headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise credentials_exception
    user = await DatabaseTransactions(pool)\
        .select('''SELECT * FROM users WHERE username = '{}' ''', token_data.username)
    if user is None:
        raise credentials_exception
    return user
