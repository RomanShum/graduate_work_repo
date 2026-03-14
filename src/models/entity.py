import uuid

from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID

from db import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class Room(Base):
    __tablename__ = 'room'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator = Column(UUID(as_uuid=True), nullable=False)
    film_id = Column(UUID(as_uuid=True), nullable=False)
    is_playing= Column(Boolean, default=False)
    current_time= Column(Float, default=False)
    created_at= Column(DateTime, default=datetime.utcnow)

    # user = relationship("User", back_populates="rooms")

class UserRoom(Base):
    __tablename__ = "user_room"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # user = relationship("User", back_populates="roles")
    # room = relationship("Room", back_populates="rooms")



class ChatMessage(Base):
    __tablename__ = 'chat_message'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id", ondelete="CASCADE"), nullable=False)
    message= Column(String(255), nullable=False)
    created_at= Column(DateTime, default=datetime.utcnow)

    # room = relationship("Room", back_populates="messages")
    # user = relationship("User", back_populates="chat_messages")


class Friend(Base):
    __tablename__ = 'friend'
    id= Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    friend_id = Column(UUID(as_uuid=True), nullable=False)
    login= Column(String(255), nullable=False)
    first_name= Column(String(255), nullable=False)
    last_name= Column(String(255), nullable=False)
    in_favorites= Column(Boolean, default=False)

    # user = relationship("User", back_populates="friends")

class VideoAction(Base):
    __tablename__ = 'video_action'

    id= Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    action= Column(String(255), nullable=False)
    time= Column(Boolean, default=False)
    created_at= Column(DateTime, default=datetime.utcnow)

    # user = relationship("User", back_populates="friends")

# class Film(Base):
#     __tablename__ = 'films'
#     id: str
#     title: str
#     description: str | None = None
#     creation_date: str | None = None
#     rating: float | None = None
#     type: str
#     created: str
#     modified: str

#
# class User(Base):
#     __tablename__ = 'users'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
#     login = Column(String(255), unique=True, nullable=False)
#     password = Column(String(255), nullable=False)
#     first_name = Column(String(50))
#     last_name = Column(String(50))
#     email = Column(String(50), unique=True, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     is_superuser = Column(Boolean, default=False)
#
#     def __init__(self, login: str, password: str, first_name: str, last_name: str, email: str, is_superuser: bool = False) -> None:
#         self.login = login
#         self.password = generate_password_hash(password)
#         self.first_name = first_name
#         self.last_name = last_name
#         self.is_superuser = is_superuser
#         self.email = email
#
#     def check_password(self, password: str) -> bool:
#         return check_password_hash(self.password, password)
#
#     def __repr__(self) -> str:
#         return f'<User {self.login}>'
#
#     roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
#
#
# class LoginHistory(Base):
#     __tablename__ = "login_history"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), nullable=False)
#     user_agent = Column(String(512), nullable=False)
#     login_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
#
#
# class Role(Base):
#     __tablename__ = "roles"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
#     name = Column(String(50), unique=True, nullable=False)
#     description = Column(String(255), nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#
#     users = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
#
#
# class UserRole(Base):
#     __tablename__ = "user_roles"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
#     assigned_at = Column(DateTime, default=datetime.utcnow)
#
#     user = relationship("User", back_populates="roles")
#     role = relationship("Role", back_populates="users")
