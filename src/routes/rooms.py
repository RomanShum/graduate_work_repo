from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import CurrentUser, get_current_user, notification_client, NotificationClient, get_notification_client
from db import get_session

from services.room_service import create_room_service, get_friends_service, get_room_service, join_room_service, \
    leave_room_service, \
    get_room_users_service, send_message_service, get_chat_history_service, video_action_service, \
    get_video_state_service, ActionEnum

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("")
async def create_room(
        film_id: str | None = None,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
        notification_client: NotificationClient = Depends(get_notification_client)
):
    """Создать новую комнату"""
    return await create_room_service(film_id=film_id, current_user=current_user, db=db,
                                     notification_client=notification_client)


@router.get("/friends")
async def list_friends(
        film_id: str | None = None,
        limit: int = 20,
        db: AsyncSession = Depends(get_session),
        current_user: CurrentUser = Depends(get_current_user),
):
    """Получить список друзей пользователя."""
    return await get_friends_service(film_id=film_id, limit=limit, db=db, current_user=current_user)


@router.get("/{room_id}")
async def get_room(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Получить информацию о комнате"""
    return await get_room_service(room_id=room_id, db=db)


@router.post("/{room_id}/join")
async def join_room(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Присоединиться к комнате"""
    return await join_room_service(room_id=room_id, db=db, current_user=current_user)


@router.post("/{room_id}/leave")
async def leave_room(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Покинуть комнату"""
    return await leave_room_service(db=db, current_user=current_user, room_id=room_id)


@router.get("/{room_id}/users")
async def get_room_users(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Получить список пользователей в комнате"""
    return await get_room_users_service(room_id=room_id, db=db)


@router.post("/{room_id}/chat")
async def send_message(
        room_id: str,
        message: str = "",
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Отправить сообщение в чат"""
    return await send_message_service(room_id=room_id, message=message, current_user=current_user, db=db)


@router.get("/{room_id}/chat")
async def get_chat_history(
        room_id: str,
        limit: int = 50,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Получить историю чата"""
    return await get_chat_history_service(room_id=room_id, limit=limit, db=db)


@router.post("/{room_id}/video")
async def video_action(
        room_id: str,
        action: ActionEnum,
        time: float,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Записать действие с видео"""
    return await video_action_service(room_id=room_id, action=action, time=time, db=db)


@router.get("/{room_id}/video/state")
async def get_video_state(
        room_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
):
    """Получить текущее состояние видео"""
    return await get_video_state_service(room_id=room_id, db=db)
