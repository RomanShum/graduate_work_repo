from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import User
from schemas.entity import RoleCreate, AssignRole, CheckPermission
from core.superuser import is_superuser
from services.role_service import create_role_service, get_all_roles_service, get_role_service, update_role_service, \
    delete_role_service, assign_role_to_user_service, revoke_role_from_user_service, check_user_permission_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleCreate, status_code=status.HTTP_201_CREATED, summary='Создаёт новую роль')
async def create_role(
        role_data: RoleCreate,
        db: AsyncSession = Depends(get_session),
        _: User = Depends(is_superuser)
):
    """
    Создаёт новую роль.
    """
    return await create_role_service(db, role_data)


@router.get("/", response_model=list[RoleCreate], status_code=status.HTTP_200_OK,
            summary='Возвращает список всех ролей')
async def get_all_roles(
        db: AsyncSession = Depends(get_session)
):
    """
    Возвращает список всех ролей.
    """
    return await get_all_roles_service(db)


@router.get("/{role_id}", response_model=RoleCreate, status_code=status.HTTP_200_OK,
            summary='Возвращает роль по её уникальному идентификатору')
async def get_role(
        role_id: str,
        db: AsyncSession = Depends(get_session)
):
    """
    Возвращает роль по её уникальному идентификатору.
    """
    return await get_role_service(db, role_id)


@router.patch("/{role_id}", response_model=RoleCreate, status_code=status.HTTP_200_OK,
              summary='Обновляет существующую роль')
async def update_role(
        role_id: str,
        role_data: RoleCreate,
        db: AsyncSession = Depends(get_session),
        _: User = Depends(is_superuser)
):
    """
    Обновляет существующую роль.
    """
    return await update_role_service(db, role_id, role_data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, summary='Удаляет роль по её ID')
async def delete_role(
        role_id: str,
        db: AsyncSession = Depends(get_session),
        _: User = Depends(is_superuser)
):
    """
    Удаляет роль по её ID.
    """
    return await delete_role_service(db, role_id)


@router.post("/assign", status_code=status.HTTP_200_OK, summary='Назначает роль пользователю')
async def assign_role_to_user(
        assign_data: AssignRole,
        db: AsyncSession = Depends(get_session),
        _: User = Depends(is_superuser)
):
    """
    Назначает роль пользователю.
    """
    return await assign_role_to_user_service(db, assign_data)


@router.post("/revoke", status_code=status.HTTP_200_OK, summary='Отзыв роли у пользователя')
async def revoke_role_from_user(
        assign_data: RoleCreate,
        db: AsyncSession = Depends(get_session),
        _: User = Depends(is_superuser)
):
    """
    Отзыв роли у пользователя.
    """
    return await revoke_role_from_user_service(db, assign_data)


@router.get("/check-permission/", status_code=status.HTTP_200_OK,
            summary='Проверяет, имеет ли пользователь указанную роль')
async def check_user_permission(
        assign_data: CheckPermission,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(is_superuser)
):
    """
    Проверяет, имеет ли пользователь указанную роль.
    """
    return await check_user_permission_service(db, assign_data, current_user)
