from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
import httpx
from models.entity import Room, UserRoom, ChatMessage, Friend

from dependencies import CurrentUser, notification_client, NotificationClient
from models.entity import Room
import logging
from core.settings import Settings
from enum import Enum

settings = Settings()
logger = logging.getLogger(__name__)


class ActionEnum(Enum):
    play = "play"
    pause = "pause"
    seek = "seek"


async def create_room_service(db: AsyncSession, current_user: CurrentUser, film_id: str, notification_client: NotificationClient):
    room = Room(
        creator=current_user.id,
        film_id=film_id
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)

    friends = await get_friends_service(film_id=film_id, db=db, current_user=current_user)
    for friend in friends:
        if friend.in_favorites:
            await notification_client.send_event(friend.id, room.id)

    logger.info(f"Комната создана: {room.id} (создатель: {current_user.login})")
    return {"id": room.id, "creator": current_user.login}


async def get_friends_service(film_id: str, db: AsyncSession, current_user: CurrentUser, limit: int = 20):
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


async def get_room_service(db: AsyncSession, room_id: str):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    return room


async def join_room_service(db: AsyncSession, room_id: str, current_user: CurrentUser):
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


async def leave_room_service(db: AsyncSession, room_id: str, current_user: CurrentUser):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if room:
        result = await db.execute(select(UserRoom).where(Room.id == room_id).where(UserRoom.user_id == current_user.id))
        await result.delete()
        await db.commit()
        logger.info(f"{current_user.login} покинул комнату {room_id}")

    return {"status": "ok", "message": f"{current_user.login} покинул комнату"}


async def get_room_users_service(db: AsyncSession, room_id: str):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    result = await db.execute(select(UserRoom).where(Room.id == room_id))
    user_rooms = result.scalars().all()
    return {"users": [user.user_id for user in user_rooms]}


async def send_message_service(db: AsyncSession, room_id: str, current_user: CurrentUser, message: str):
    chat_message = ChatMessage(
        user_id=current_user.id,
        room_id=room_id,
        message=message
    )
    db.add(chat_message)
    await db.commit()
    await db.refresh(chat_message)
    return chat_message


async def get_chat_history_service(db: AsyncSession, room_id: str, limit: int = 100):
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


async def video_action_service(db: AsyncSession, room_id: str, time: float, action: ActionEnum):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    if action == ActionEnum.play:
        room.is_playing = True
        room.current_time = time
    elif action == ActionEnum.pause:
        room.is_playing = False
        room.current_time = time
    elif action == ActionEnum.seek:
        room.current_time = time

    return {"status": "ok", "action": action, "time": time}


async def get_video_state_service(db: AsyncSession, room_id: str):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    return {
        "is_playing": room.is_playing,
        "current_time": room.current_time
    }
