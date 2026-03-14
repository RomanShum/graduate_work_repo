from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from schemas.entity import UserCreate, UserInDB, Token, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from models.entity import User
from services.user_service import authenticate_user, get_user_login_history, refresh_user_token, logout_user, \
    update_user, get_user_info
from db.postgres import get_session
import services.user_service as user_service
from schemas.entity import LoginHistorySchema, RefreshTokenRequest
from services.user_service import get_current_user

router = APIRouter(prefix='/user', tags=['user'])


@router.post('/signup', response_model=UserInDB, status_code=status.HTTP_201_CREATED,
             summary='Регистрация пользователя')
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_session)) -> UserInDB:
    """
    Создание пользователя
    """
    return await user_service.create_user(db, user_create)


@router.post("/login", response_model=Token,
             status_code=status.HTTP_200_OK,
             summary='Аутентификация пользователя')
async def login_for_access_token(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_session)
):
    """
    Авторизация пользователя
    """
    return await authenticate_user(db, form_data.username, form_data.password, request.headers.get('User-Agent', ''))


@router.get("/login-history", response_model=list[LoginHistorySchema], status_code=status.HTTP_200_OK,
            summary='Получение истории входов пользователя')
async def get_login_history(
        db: AsyncSession = Depends(get_session),
        page_size: int = Query(title='page size', description='Page size', default=10, ge=1, le=100),
        page_number: int = Query(title='page number', description='Page number', default=1, ge=1),
        current_user: User = Depends(get_current_user)
):
    """
    Получение истории входов пользователя
    """
    return await get_user_login_history(db, current_user.id, page_size, page_number)


@router.get("/get/{user_id}", response_model=UserInDB, status_code=status.HTTP_200_OK,
            summary='Получение пользователя')
async def get_user(
        user_id: str,
        db: AsyncSession = Depends(get_session)
):
    """
    Получение пользователя
    """
    return await get_user_info(db, user_id)


@router.post('/refresh', response_model=Token, status_code=status.HTTP_200_OK, summary='Обновление токена')
async def refresh_access_token(
        request: Request,
        refresh_token: RefreshTokenRequest,
        db: AsyncSession = Depends(get_session)
):
    """
    Обновление токена
    """
    user_agent = request.headers.get('User-Agent', '')
    return await refresh_user_token(user_agent, refresh_token.refresh_token, db)


@router.post('/logout', status_code=status.HTTP_200_OK, summary='Выход пользователя')
async def logout(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """
    Выход пользователя
    """
    user_agent = request.headers.get('User-Agent', '')
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Authorization header missing")

    access_token = auth_header[7:]
    return await logout_user(user_agent, current_user.id, access_token)


@router.patch("/me", response_model=UserInDB, summary='Обновление текущего пользователя')
async def update_current_user(
        user_update: UserUpdate,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Обновление текущего пользователя
    """
    return await update_user(
        db=db,
        user=current_user,
        login=user_update.login,
        password=user_update.password
    )
