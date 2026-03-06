from models.entity import Favorite
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional


async def get_favorite_from_db(user_id: UUID, film_id: UUID) -> Optional[Favorite]:
    return await Favorite.find_one(Favorite.user_id == user_id, Favorite.film_id == film_id)

async def get_favorite( user_id: UUID, film_id: UUID) -> Optional[Favorite]:
    favorite = await get_favorite_from_db(user_id=user_id, film_id=film_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    return favorite

async def set_favorite( user_id: UUID, film_id: UUID) -> Optional[Favorite]:
    favorite = await get_favorite_from_db(user_id=user_id, film_id=film_id)
    if not favorite:
        favorite = Favorite(user_id=user_id, film_id=film_id)
        return await favorite.insert()
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail='Уже существует'
    )


async def delete_favorite( user_id: UUID, film_id: UUID) -> bool:
    favorite = await get_favorite_from_db(user_id, film_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    await favorite.delete()
    return True