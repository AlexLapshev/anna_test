from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from loguru import logger
from typing import Optional


SECRET_KEY = '''5010C61629C8F7BA65FAD18ECB2DB472D093D7C820503AC2C238ECED7DFCD9414A0F31868F672E85F2032421D7CB3AD7CF8EA604659F39F64DC77981DF1AC75A'''


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, secret_key=SECRET_KEY) -> str:
    logger.debug('creating access token')
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm='HS256')
    return encoded_jwt


def decode_token(token, secret_key=SECRET_KEY):
    logger.debug('decoding token')
    try:
        decoded_jwt = jwt.decode(token, secret_key, algorithms='HS256')
        return decoded_jwt
    except ExpiredSignatureError as e:
        logger.debug('expired token')
        raise ExpiredSignatureError('Token has expired')
    except JWTError as e:
        logger.debug('invalid token')
        raise ValueError('Invalid basic auth credentials')
