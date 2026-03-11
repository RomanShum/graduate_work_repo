from typing import Dict
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWTError
from pydantic import BaseModel


class RoomManager:
    """Менеджер для хранения комнат в памяти (для простоты)"""

    def __init__(self):
        self.rooms: Dict[str, dict] = {}
        self.room_messages: Dict[str, list] = {}

    def create_room(self, room_data: dict) -> dict:
        room_id = room_data["id"]
        self.rooms[room_id] = room_data
        self.room_messages[room_id] = []
        return room_data

    def get_room(self, room_id: str) -> dict | None:
        return self.rooms.get(room_id)

    def update_room(self, room_id: str, data: dict) -> dict | None:
        if room_id in self.rooms:
            self.rooms[room_id].update(data)
            return self.rooms[room_id]
        return None

    def delete_room(self, room_id: str):
        if room_id in self.rooms:
            del self.rooms[room_id]
        if room_id in self.room_messages:
            del self.room_messages[room_id]

    def add_user_to_room(self, room_id: str, user: dict) -> bool:
        if room_id in self.rooms:
            users = self.rooms[room_id]["users"]
            for existing_user in users:
                if existing_user["id"] == user["id"]:
                    return False
            users.append(user)
            return True
        return False

    def remove_user_from_room(self, room_id: str, user_id: str):
        if room_id in self.rooms:
            users = self.rooms[room_id]["users"]
            self.rooms[room_id]["users"] = [u for u in users if u["id"] != user_id]

    def get_room_users(self, room_id: str) -> list:
        if room_id in self.rooms:
            return self.rooms[room_id]["users"]
        return []

    def add_message(self, room_id: str, message: dict):
        if room_id in self.room_messages:
            self.room_messages[room_id].append(message)
            if len(self.room_messages[room_id]) > 100:
                self.room_messages[room_id] = self.room_messages[room_id][-100:]

    def get_messages(self, room_id: str, limit: int = 50) -> list:
        if room_id in self.room_messages:
            return self.room_messages[room_id][-limit:]
        return []

    def update_video_state(self, room_id: str, video_state: dict):
        if room_id in self.rooms:
            self.rooms[room_id]["video_state"] = video_state

    def get_video_state(self, room_id: str) -> dict:
        if room_id in self.rooms:
            return self.rooms[room_id].get("video_state", {})
        return {}


room_manager = RoomManager()


class CurrentUser(BaseModel):
    id: str
    login: str


http_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> CurrentUser:
    secret_key = os.getenv("SECRET_KEY", "your-super-secret-key")
    algorithm = os.getenv("ALGORITHM", "HS256")

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