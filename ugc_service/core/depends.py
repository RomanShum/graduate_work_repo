from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from core.settings import settings
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Depends
from jose import jwt, JWTError
from uuid import UUID
from typing import Annotated

def get_uuid_user_id(token:HTTPAuthorizationCredentials, credentials_exception: HTTPException) -> UUID:
    payload = jwt.decode(token.credentials, settings.secret_key,
                         algorithms=[settings.algorithm])
    user_id: str = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    return UUID(user_id)

async def get_current_user(
        token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]
) -> UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка аутентификации"
    )
    try:
        return get_uuid_user_id(token, credentials_exception)
    except JWTError:
        raise credentials_exception