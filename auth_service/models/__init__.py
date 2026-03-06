# Явная загрузка всех моделей для SQLAlchemy registry
from models.entity import User, Role, UserRole
from db.postgres import Base

# Это гарантирует, что все модели будут известны SQLAlchemy
__all__ = ["User", "Role", "UserRole", "Base"]
