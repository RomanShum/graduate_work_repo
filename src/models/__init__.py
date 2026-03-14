# Явная загрузка всех моделей для SQLAlchemy registry
from models.entity import Room, UserRoom, ChatMessage, Friend
from db import Base

# Это гарантирует, что все модели будут известны SQLAlchemy
__all__ = ["Room", "UserRoom", "ChatMessage", "Friend", "VideoAction"]
