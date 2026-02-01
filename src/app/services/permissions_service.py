from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user_permissions import UserPermissions
from app.schemas.permissions import SaveSettingsRequest


async def get_permissions_by_manager(
    subdomain: str,
    manager_id: int,
    session: AsyncSession
) -> Optional[UserPermissions]:
    """
    Получить настройки permissions для менеджера

    Args:
        subdomain: Субдомен amoCRM
        manager_id: ID менеджера
        session: Асинхронная сессия БД

    Returns:
        UserPermissions или None, если настройки не найдены
    """
    stmt = select(UserPermissions).where(
        UserPermissions.subdomain == subdomain,
        UserPermissions.manager_id == manager_id
    )

    result = await session.execute(stmt)
    permissions = result.scalar_one_or_none()

    return permissions


async def save_permissions(
    request: SaveSettingsRequest,
    session: AsyncSession
) -> UserPermissions:
    """
    Сохранить настройки permissions для менеджера.
    Если настройки уже существуют - удаляет старые и создаёт новые.

    Args:
        request: Запрос с настройками
        session: Асинхронная сессия БД

    Returns:
        Созданная запись UserPermissions
    """
    # Удаляем старые настройки, если они есть
    await delete_permissions(
        subdomain=request.subdomain,
        manager_id=request.manager_id,
        session=session
    )

    # Создаём новую запись
    permissions_dict = request.permissions.model_dump()

    new_permissions = UserPermissions(
        subdomain=request.subdomain,
        manager_id=request.manager_id,
        permissions=permissions_dict
    )

    session.add(new_permissions)
    await session.commit()
    await session.refresh(new_permissions)

    return new_permissions


async def delete_permissions(
    subdomain: str,
    manager_id: int,
    session: AsyncSession
) -> bool:
    """
    Удалить настройки permissions для менеджера

    Args:
        subdomain: Субдомен amoCRM
        manager_id: ID менеджера
        session: Асинхронная сессия БД

    Returns:
        True, если запись была удалена, False если записи не было
    """
    stmt = delete(UserPermissions).where(
        UserPermissions.subdomain == subdomain,
        UserPermissions.manager_id == manager_id
    )

    result = await session.execute(stmt)
    await session.commit()

    deleted = result.rowcount > 0

    return deleted


async def get_all_permissions_for_subdomain(
    subdomain: str,
    session: AsyncSession
) -> list[UserPermissions]:
    """
    Получить все настройки permissions для субдомена

    Args:
        subdomain: Субдомен amoCRM
        session: Асинхронная сессия БД

    Returns:
        Список всех настроек для субдомена
    """
    stmt = select(UserPermissions).where(
        UserPermissions.subdomain == subdomain
    ).order_by(UserPermissions.manager_id.asc())

    result = await session.execute(stmt)
    permissions_list = result.scalars().all()

    return list(permissions_list)
