from fastapi import APIRouter, Depends, Request, status
from uuid import UUID
from models.entity import Review, ReviewRequest
from services import review_service
from core.depends import get_current_user
from typing import Annotated, Optional

router = APIRouter(prefix='/review', tags=['reviews'])


@router.get("/{film_id}/", response_model=Review)
async def get_review(
    film_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Review:
    return await review_service.get_review(film_id = film_id, user_id=user_id)

@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review(
    body: ReviewRequest,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Optional[Review]:
    return await review_service.create_review(film_id=body.film_id, user_id=user_id, review_value=body.review_value)

@router.patch("/", response_model=Review, status_code=status.HTTP_200_OK)
async def update_review(
    body: ReviewRequest,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> Optional[Review]:
    return await review_service.update_review(film_id=body.film_id, user_id=user_id, review_value=body.review_value)


@router.delete("/{film_id}/", status_code=status.HTTP_200_OK)
async def delete_review(
    film_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user)]
) -> bool:
    return await review_service.delete_review(film_id = film_id, user_id=user_id)
