from fastapi import Depends, HTTPException, status
from models.entity import User
from services.user_service import get_current_user


async def is_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права суперпользователя"
        )
    return user
