from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from sqlalchemy.future import select
from dependencies import CurrentUser, get_current_user, notification_client, NotificationClient, get_notification_client
from db import get_session
from core.settings import Settings
from models.entity import Room, UserRoom, ChatMessage, Friend
import logging

router = APIRouter(prefix="/api/rooms", tags=["rooms"])
settings = Settings()
logger = logging.getLogger(__name__)


@router.post("")
async def create_room(
        film_id: str | None = None,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
        notification_client: NotificationClient = Depends(get_notification_client)
):
    """Создать новую комнату"""

    room = Room(
        creator=current_user.id,
        film_id=film_id
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)

    friends = await list_friends(film_id=film_id, db=db, current_user=current_user)
    for friend in friends:
        if friend.in_favorites:
            await notification_client.send_event(friend.id, room.id)

    logger.info(f"Комната создана: {room.id} (создатель: {current_user.login})")
    return {"id": room.id, "creator": current_user.login}


@router.get("/films")
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

    films = [dict(row._mapping) for row in rows]

    return films


@router.get("/friends")
async def list_friends(
        film_id: str | None = None,
        limit: int = 20,
        db: AsyncSession = Depends(get_session),
        current_user: CurrentUser = Depends(get_current_user),
):
    """Получить список друзей пользователя."""
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

    if film_id:
        ugc_base = settings.ugc_url
        url = f"{ugc_base}/api/v1/favorite/film/{film_id}/users"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    favorite_user_ids = set(str(uid) for uid in data)
        except Exception:
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
        db: AsyncSession = Depends(get_session)
):
    """Получить информацию о комнате"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    return room


@router.post("/{room_id}/join")
async def join_room(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Присоединиться к комнате"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    result = await db.execute(select(UserRoom).where(Room.id == room_id))
    user_rooms = result.scalars().all()

    if not room:
        logger.info(f"Комната {room_id} не найдена")
        raise HTTPException(status_code=404, detail="Комната не найдена")

    if not current_user.id in [user_room.user_id for user_room in user_rooms]:
        room = UserRoom(
            user_id=current_user.id,
            room_id=room_id
        )
        db.add(room)
        await db.commit()
        await db.refresh(room)
        logger.info(f"{current_user.login} присоединился к комнате {room_id}")
    else:
        logger.info(f"{current_user.login} уже в комнате {room_id}")

    return room


@router.post("/{room_id}/leave")
async def leave_room(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Покинуть комнату"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if room:
        result = await db.execute(select(UserRoom).where(Room.id == room_id).where(UserRoom.user_id == current_user.id))
        await result.delete()
        await db.commit()
        logger.info(f"{current_user.login} покинул комнату {room_id}")

    return {"status": "ok", "message": f"{current_user.login} покинул комнату"}


@router.get("/{room_id}/users")
async def get_room_users(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Получить список пользователей в комнате"""

    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    result = await db.execute(select(UserRoom).where(Room.id == room_id))
    user_rooms = result.scalars().all()
    return {"users": [user.user_id for user in user_rooms]}


@router.post("/{room_id}/chat")
async def send_message(
        room_id: str,
        message: str = "",
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Отправить сообщение в чат"""

    chat_message = ChatMessage(
        user_id=current_user.id,
        room_id=room_id,
        message=message
    )
    db.add(chat_message)
    await db.commit()
    await db.refresh(chat_message)
    return chat_message


@router.get("/{room_id}/chat")
async def get_chat_history(
        room_id: str,
        limit: int = 50,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Получить историю чата"""
    result = await db.execute(
        text("""
            SELECT *, users.login as username FROM chat_message
            JOIN users ON users.id = chat_message.user_id
            WHERE room_id = :room_id
            ORDER BY chat_message.created_at ASC
            LIMIT :limit
        """),
        {"room_id": room_id, "limit": limit}
    )
    rows = result.fetchall()
    messages = [dict(row._mapping) for row in rows]
    return messages


@router.post("/{room_id}/video")
async def video_action(
        room_id: str,
        action: str,
        time: float,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Записать действие с видео"""

    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

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
        db: AsyncSession = Depends(get_session)
):
    """Получить текущее состояние видео"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    return {
        "is_playing": room.is_playing,
        "current_time": room.current_time
    }
