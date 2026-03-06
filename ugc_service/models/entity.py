from uuid import UUID
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from core.settings import Settings

settings = Settings()

class FavoriteRequest(Document):
    film_id: UUID = Indexed(UUID)

class Favorite(FavoriteRequest):
    user_id: UUID = Indexed(UUID)

class LikeRequest(Document):
    like_value: int = Field(..., ge=1, le=10)
    film_id: UUID = Indexed(UUID)

class Like(LikeRequest):
    user_id: UUID = Indexed(UUID)

class ReviewRequest(Document):
    film_id: UUID = Indexed(UUID)
    review_value: str = Field(
        ...,
        min_length=settings.min_review_length,
        max_length=settings.max_review_length
    )
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

class Review(ReviewRequest):
    user_id: UUID = Indexed(UUID)