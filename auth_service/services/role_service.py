from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.entity import User, Role, UserRole
from schemas.entity import RoleCreate
from sqlalchemy.future import select


async def create_role_service(db: AsyncSession, role_data: RoleCreate):
    result = await db.execute(select(Role).where(Role.name == role_data.name))
    existing_role = result.scalar_one_or_none()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Название роли уже существует"
        )

    role = Role(name=role_data.name, description=role_data.description)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def get_all_roles_service(db: AsyncSession):
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return roles


async def get_role_service(db: AsyncSession, role_id: int):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")
    return role


async def update_role_service(db: AsyncSession, role_id: int, role_data: RoleCreate):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")

    if role_data.name:
        existing = await db.execute(select(Role).where(Role.name == role_data.name))
        if existing.scalar_one_or_none() and existing.scalar().id != role_id:
            raise HTTPException(status_code=400, detail="Название роли уже существует")

        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description

    await db.commit()
    await db.refresh(role)
    return role


async def delete_role_service(db: AsyncSession, role_id: int):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")

    await db.delete(role)
    await db.commit()


async def assign_role_to_user_service(db: AsyncSession, assign_data):
    user_result = await db.execute(select(User).where(User.id == assign_data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверим, существует ли роль
    role_result = await db.execute(select(Role).where(Role.id == assign_data.role_id))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")

    # Проверим, не назначена ли уже роль
    link_result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == assign_data.user_id,
            UserRole.role_id == assign_data.role_id
        )
    )
    existing = link_result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="У данного пользователя уже есть эта роль")

    user_role = UserRole(user_id=assign_data.user_id, role_id=assign_data.role_id)
    db.add(user_role)
    await db.commit()
    return {"detail": "Success"}


async def revoke_role_from_user_service(db: AsyncSession, assign_data):
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == assign_data.user_id,
            UserRole.role_id == assign_data.role_id
        )
    )
    user_role = result.scalar_one_or_none()
    if not user_role:
        raise HTTPException(status_code=404, detail="Не удалось найти роль пользователя")

    await db.delete(user_role)
    await db.commit()
    return {"detail": "Success"}


async def check_user_permission_service(db, assign_data, current_user):
    role_name, user_id = assign_data.role_name, assign_data.user_id
    target_user_id = user_id or current_user.id

    result = await db.execute(
        select(Role).join(UserRole).where(
            UserRole.user_id == str(target_user_id),
            Role.name == role_name
        )
    )
    role = result.scalar_one_or_none()
    return {"has_role": bool(role), "user_id": target_user_id, "role": role_name}
