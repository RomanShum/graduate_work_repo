from werkzeug.security import generate_password_hash
from fastapi.encoders import jsonable_encoder
from schemas.entity import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.entity import User, LoginHistory
from fastapi import HTTPException, status
from core.auth import create_access_token, create_refresh_token, decode_token
from core.settings import settings
from db.redis import get_redis
from redis.asyncio import Redis
from datetime import timedelta, timezone, datetime
from fastapi.security import HTTPBearer
from fastapi import Depends
from db.postgres import get_session
from jose import jwt, JWTError


async def create_user(db: AsyncSession, user_create: UserCreate):
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, login: str, password: str, user_agent: str) -> User | None:
    result = await db.execute(select(User).where(User.login == login))
    user = result.scalar_one_or_none()
    if not user or not user.check_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин или пароль'
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(data={"sub": user.login})
    user_id = str(user.id)

    redis: Redis = await get_redis()
    key = f'refresh:{user_id}:{user_agent}'

    await redis.set(
        key,
        refresh_token,
        ex=settings.REFRESH_TOKEN_EXPIRE_SECONDS
    )

    login_record = LoginHistory(
        user_id=user_id,
        user_agent=user_agent,
        login_at=datetime.now(timezone.utc)
    )
    db.add(login_record)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


async def get_user_login_history(db: AsyncSession, user_id: str, page_size: int, page_number: int):
    query = (select(LoginHistory).
             where(LoginHistory.user_id == user_id).
             limit(page_size).
             offset((page_number - 1) * page_size).
             order_by(LoginHistory.login_at.desc()))

    result = await db.execute(query)
    history = result.scalars().all()
    return history


async def get_current_user(
        token: str = Depends(HTTPBearer()),
        db: AsyncSession = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка аутентификации"
    )
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        login: str = payload.get("sub")
        unique_id_token: str = payload.get("id")
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.login == login))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    redis = await get_redis()
    is_blocked = await redis.get(f"blocklist:{unique_id_token}")
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен заблокирован"
        )

    return user


async def refresh_user_token(
        user_agent: str,
        refresh_token: str,
        db: AsyncSession):
    redis = await get_redis()
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный токен"
        )

    login = payload.get("sub")
    if not login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный токен"
        )

    user_result = await db.execute(select(User).where(User.login == login))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    redis_key = f"refresh:{str(user.id)}:{user_agent}"

    stored_token = await redis.get(redis_key)

    if not stored_token or stored_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный токен"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": login}, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token(data={"sub": login})

    await redis.set(
        redis_key,
        new_refresh_token,
        ex=settings.REFRESH_TOKEN_EXPIRE_SECONDS
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


async def logout_user(user_agent: str, user_id: str, access_token: str):
    redis = await get_redis()
    redis_key = f"refresh:{user_id}:{user_agent}"

    deleted = await redis.delete(redis_key)

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error"
        )

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_id = payload.get("id")
        if token_id:
            exp = payload.get("exp")
            ttl = max(exp - int(datetime.utcnow().timestamp()), 60)
            await redis.set(f"blocklist:{token_id}", "1", ex=ttl)
    except JWTError:
        pass

    return {"detail": "Success"}


async def update_user(
        db: AsyncSession,
        user: User,
        login: str = None,
        password: str = None
):
    if login:
        result = await db.execute(select(User).where(User.login == login))
        existing_user = result.scalar_one_or_none()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой логин уже существует"
            )
        user.login = login

    if password:
        user.password = generate_password_hash(password)

    await db.commit()
    await db.refresh(user)
    return user
