# routes/rooms.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
import uuid
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import os

from dependencies import CurrentUser, get_current_user
from db import get_session

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


# Модели данных
class User(BaseModel):
    name: str
    joined_at: str = None


class Room(BaseModel):
    id: str
    creator: str
    users: List[User] = []
    film_id: str | None = None
    video_url: str = ""
    is_playing: bool = False
    current_time: float = 0
    created_at: str = None


class ChatMessage(BaseModel):
    username: str
    message: str
    timestamp: str = None


class Friend(BaseModel):
    id: str
    login: str
    first_name: str | None = None
    last_name: str | None = None
    in_favorites: bool = False


class Film(BaseModel):
    id: str
    title: str
    description: str | None = None
    creation_date: str | None = None
    rating: float | None = None
    type: str
    created: str
    modified: str


# Хранилища данных
rooms_db: Dict[str, Room] = {}
messages_db: Dict[str, List[ChatMessage]] = {}


@router.post("")
async def create_room(
    film_id: str | None = None,
    creator: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Создать новую комнату"""
    username = creator or current_user.login

    room_id = str(uuid.uuid4())[:8].upper()

    room = Room(
        id=room_id,
        creator=username,
        users=[User(name=username, joined_at=datetime.now().isoformat())],
        film_id=film_id,
        created_at=datetime.now().isoformat()
    )

    rooms_db[room_id] = room
    messages_db[room_id] = []

    print(f"✅ Комната создана: {room_id} (создатель: {username})")
    return {"id": room_id, "creator": username}


@router.get("/films", response_model=list[Film])
async def list_films(
    limit: int = 50,
    db: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить список фильмов для выбора."""
    query = text(
        """
        SELECT id,
               title,
               description,
               creation_date,
               rating,
               type,
               created,
               modified
        FROM content.film_work
        LIMIT :limit
        """
    )
    result = await db.execute(query, {"limit": limit})
    rows = result.fetchall()

    films: list[Film] = []
    for row in rows:
        films.append(
            Film(
                id=str(row.id),
                title=row.title,
                description=row.description,
                creation_date=str(row.creation_date) if row.creation_date else None,
                rating=float(row.rating) if row.rating is not None else None,
                type=row.type,
                created=str(row.created),
                modified=str(row.modified),
            )
        )

    return films


@router.get("/friends", response_model=list[Friend])
async def list_friends(
    film_id: str | None = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить список друзей пользователя.

    Для простоты считаем друзьями других пользователей из auth_service.
    Если передан film_id, помечаем, у кого фильм в избранном (по данным UGC).
    """
    # 1. Получаем других пользователей из auth_service (Postgres public.users)
    users_query = text(
        """
        SELECT id, login, first_name, last_name
        FROM public.users
        WHERE login != :login
        ORDER BY login
        LIMIT :limit
        """
    )
    result = await db.execute(users_query, {"login": current_user.login, "limit": limit})
    other_users = result.fetchall()

    favorite_user_ids: set[str] = set()

    # 2. Если указан фильм, дергаем UGC, чтобы узнать, у кого он в избранном
    if film_id:
        ugc_base = os.getenv("UGC_BASE_URL", "http://ugc:8000")
        url = f"{ugc_base}/api/v1/favorite/film/{film_id}/users"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # ожидаем список строковых UUID
                    favorite_user_ids = set(str(uid) for uid in data)
        except Exception:
            # не падаем, просто считаем, что избранных нет
            favorite_user_ids = set()

    friends: list[Friend] = []
    for row in other_users:
        user_id = str(row.id)
        friends.append(
            Friend(
                id=user_id,
                login=row.login,
                first_name=row.first_name,
                last_name=row.last_name,
                in_favorites=user_id in favorite_user_ids,
            )
        )

    return friends


@router.get("/{room_id}")
async def get_room(
    room_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить информацию о комнате"""
    room = rooms_db.get(room_id.upper())
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    return room


@router.post("/{room_id}/join")
async def join_room(
    room_id: str,
    username: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Присоединиться к комнате"""
    room_id = room_id.upper()
    room = rooms_db.get(room_id)

    username = username or current_user.login

    if not room:
        print(f"❌ Комната {room_id} не найдена")
        raise HTTPException(status_code=404, detail="Комната не найдена")

    # Проверяем, есть ли уже такой пользователь
    if not any(user.name == username for user in room.users):
        room.users.append(User(name=username, joined_at=datetime.now().isoformat()))
        print(f"👤 {username} присоединился к комнате {room_id}")
    else:
        print(f"👤 {username} уже в комнате {room_id}")

    return room


@router.post("/{room_id}/leave")
async def leave_room(
    room_id: str,
    username: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Покинуть комнату"""
    room_id = room_id.upper()
    room = rooms_db.get(room_id)

    username = username or current_user.login

    if room:
        room.users = [user for user in room.users if user.name != username]
        print(f"👋 {username} покинул комнату {room_id}")

    return {"status": "ok", "message": f"{username} покинул комнату"}


@router.get("/{room_id}/users")
async def get_room_users(
    room_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить список пользователей в комнате"""
    room_id = room_id.upper()
    room = rooms_db.get(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    return {"users": [user.name for user in room.users]}


@router.post("/{room_id}/chat")
async def send_message(
    room_id: str,
    username: str | None = None,
    message: str = "",
    current_user: CurrentUser = Depends(get_current_user),
):
    """Отправить сообщение в чат"""
    room_id = room_id.upper()

    username = username or current_user.login

    if room_id not in messages_db:
        messages_db[room_id] = []

    chat_message = ChatMessage(
        username=username,
        message=message,
        timestamp=datetime.now().isoformat()
    )

    messages_db[room_id].append(chat_message)

    # Храним только последние 100 сообщений
    if len(messages_db[room_id]) > 100:
        messages_db[room_id] = messages_db[room_id][-100:]

    return chat_message


@router.get("/{room_id}/chat")
async def get_chat_history(
    room_id: str,
    limit: int = 50,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить историю чата"""
    room_id = room_id.upper()
    room_messages = messages_db.get(room_id, [])
    return room_messages[-limit:]


@router.post("/{room_id}/video")
async def video_action(
    room_id: str,
    action: str,
    time: float,
    username: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Записать действие с видео"""
    room_id = room_id.upper()

    username = username or current_user.login
    room = rooms_db.get(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    # Обновляем состояние комнаты
    if action == "play":
        room.is_playing = True
        room.current_time = time
    elif action == "pause":
        room.is_playing = False
        room.current_time = time
    elif action == "seek":
        room.current_time = time

    return {"status": "ok", "action": action, "time": time}


@router.get("/{room_id}/video/state")
async def get_video_state(
    room_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Получить текущее состояние видео"""
    room_id = room_id.upper()
    room = rooms_db.get(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    return {
        "is_playing": room.is_playing,
        "current_time": room.current_time,
        "video_url": room.video_url
    }