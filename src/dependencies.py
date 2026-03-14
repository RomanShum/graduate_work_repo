from uuid import UUID

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


class NotificationClient:
    def __init__(self):
        self.url = settings.notification_url

    async def send_event(self, user_id: UUID, room_id: UUID):
        url = f"{self.url}/notification/v1/event/create_room"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={
                    "room_id": str(room_id),
                    "object_id": str(user_id),
                    "type": "created_room"
                }) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Notification service error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Unexpected error in auth client: {str(e)}")
            return None


notification_client = NotificationClient()


def get_notification_client() -> NotificationClient:
    return notification_client
