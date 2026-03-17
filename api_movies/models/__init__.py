# Явная загрузка всех моделей для SQLAlchemy registry
from models.entity import FilmWork
from db import Base

# Это гарантирует, что все модели будут известны SQLAlchemy
__all__ = ["FilmWork"]
