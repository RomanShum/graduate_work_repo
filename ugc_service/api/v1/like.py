from fastapi import APIRouter, Depends, Request, status
from uuid import UUID
from models.entity import Like, LikeRequest
from services import like_service
from core.depends import get_current_user
from typing import Annotated, Optional

router = APIRouter(prefix='/like', tags=['likes'])


@router.get("/{film_id}/", response_model=Like)
async def get_like(
    film_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Like:
    return await like_service.get_like(film_id=film_id, user_id=user_id)


@router.post("/", response_model=Like, status_code=status.HTTP_201_CREATED)
async def create_like(
    body: LikeRequest,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Optional[Like]:
    return await like_service.create_like(film_id=body.film_id, user_id=user_id, like_value=body.like_value)

@router.patch("/", response_model=Like, status_code=status.HTTP_200_OK)
async def update_like(
    body: LikeRequest,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Optional[Like]:
    return await like_service.update_like(film_id=body.film_id, user_id=user_id, like_value=body.like_value)


@router.delete("/{film_id}/", status_code=status.HTTP_200_OK)
async def delete_like(
    film_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> bool:
    return await like_service.delete_like(film_id=film_id, user_id=user_id)
