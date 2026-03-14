import uuid

from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID

from db import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Room(Base):
    __tablename__ = 'room'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator = Column(UUID(as_uuid=True), nullable=False)
    film_id = Column(UUID(as_uuid=True), nullable=False)
    is_playing = Column(Boolean, default=False)
    current_time = Column(Float, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRoom(Base):
    __tablename__ = "user_room"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = 'chat_message'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id", ondelete="CASCADE"), nullable=False)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Friend(Base):
    __tablename__ = 'friend'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    friend_id = Column(UUID(as_uuid=True), nullable=False)
    login = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    in_favorites = Column(Boolean, default=False)


class VideoAction(Base):
    __tablename__ = 'video_action'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(255), nullable=False)
    time = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
