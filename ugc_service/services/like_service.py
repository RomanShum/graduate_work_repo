from models.entity import Like
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional

async def get_like_from_db(user_id: UUID, film_id: UUID) -> Optional[Like]:
    return await Like.find_one(Like.user_id == user_id, Like.film_id == film_id)

async def get_like( user_id: UUID, film_id: UUID):
    like = await get_like_from_db(user_id, film_id)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    return like

async def create_like( user_id: UUID, film_id: UUID, like_value: int) -> Optional[Like]:
    like = await get_like_from_db(user_id=user_id, film_id=film_id)
    if like:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Уже существует'
        )
    like = Like(user_id=user_id, film_id=film_id, like_value=like_value)
    return await like.insert()

async def update_like( user_id: UUID, film_id: UUID, like_value: int) -> Optional[Like]:
    like = await get_like_from_db(user_id, film_id)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    like.like_value = like_value
    return await like.save()

async def delete_like( user_id: UUID, film_id: UUID) -> bool:
    like = await get_like_from_db(user_id, film_id)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    await like.delete()
    return True