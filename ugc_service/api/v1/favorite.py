from fastapi import APIRouter, Depends, Request, status
from uuid import UUID
from models.entity import Favorite, FavoriteRequest
from services import favorite_service
from core.depends import get_current_user
from typing import Annotated

router = APIRouter(prefix='/favorite', tags=['favorites'])


@router.get("/{film_id}/", response_model=Favorite)
async def get_favorite(
    film_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Favorite:
    return await favorite_service.get_favorite(film_id=film_id, user_id=user_id)


@router.put("/", response_model=Favorite, status_code=status.HTTP_201_CREATED)
async def set_favorite(
    body: FavoriteRequest,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Favorite:
    return await favorite_service.set_favorite(film_id=body.film_id, user_id=user_id)


@router.delete("/{film_id}/", status_code=status.HTTP_200_OK)
async def delete_favorite(
    film_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> bool:
    return await favorite_service.delete_favorite(film_id=film_id, user_id=user_id)
