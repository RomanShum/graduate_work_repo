from models.entity import Review
from fastapi import HTTPException, status
from datetime import datetime
from uuid import UUID
from typing import Optional

async def get_review_from_db(user_id:UUID, film_id:UUID) -> Optional[Review]:
    return await Review.find_one(Review.user_id == user_id, Review.film_id == film_id)

async def get_review( user_id: UUID, film_id: UUID):
    review = await get_review_from_db(user_id=user_id, film_id=film_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    return review

async def create_review( user_id: UUID, film_id: UUID, review_value: str) -> Optional[Review]:
    review = await get_review_from_db(user_id=user_id, film_id=film_id)
    if review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Уже существует'
        )
    review = Review(user_id=user_id, film_id=film_id, review_value=review_value)
    return await review.insert()

async def update_review( user_id: UUID, film_id: UUID, review_value: str) -> Optional[Review]:
    review = await get_review_from_db(user_id=user_id, film_id=film_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    review.review_value = review_value
    review.updated = datetime.utcnow()
    return await review.save()

async def delete_review( user_id: UUID, film_id: UUID) -> bool:
    review = await get_review_from_db( user_id=user_id, film_id=film_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не найдено'
        )
    await review.delete()
    return True