from uuid import UUID
from beanie import Document, Indexed
from pydantic import Field, BaseModel
from datetime import datetime
from core.settings import Settings
from abc import ABC

settings = Settings()


class BaseEvent(BaseModel, ABC):
    type: str


class Notification(Document):
    id: UUID = Indexed(UUID)
    object_id: UUID | None = None
    room_id: UUID | None = None
    type: str
    created_at: datetime = Field(default_factory=datetime.now)
    read: bool = Field(default=False)


class UserRegistrationEvent(BaseEvent):
    object_id: UUID
    username: str
    email: str
    registration_date: datetime = Field(default_factory=datetime.now)


class NewContentEvent(BaseEvent):
    object_id: UUID
    release_date: datetime = Field(default_factory=datetime.now)

class CreateRoomEvent(BaseEvent):
    object_id: UUID
    room_id: UUID
