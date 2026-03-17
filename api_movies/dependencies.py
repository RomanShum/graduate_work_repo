from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWTError
from pydantic import BaseModel
import aiohttp
from core.settings import Settings
import logging

settings = Settings()
logger = logging.getLogger(__name__)


class CurrentUser(BaseModel):
    id: str
    login: str


http_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> CurrentUser:
    secret_key = settings.SECRET_KEY
    algorithm = settings.ALGORITHM

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка аутентификации",
    )

    try:
        payload = jwt.decode(token.credentials, secret_key, algorithms=[algorithm])
        user_id = payload.get("user_id")
        login = payload.get("sub")
        if user_id is None or login is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    return CurrentUser(id=user_id, login=login)
