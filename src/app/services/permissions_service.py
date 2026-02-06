from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user_permissions import UserPermissions
from app.schemas.permissions import SaveSettingsRequest
from app.core.logging import logger


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
    logger.info(
        "DB → Запрос к БД на получение настроек | subdomain: %s, manager_id: %s",
        subdomain,
        manager_id
    )

    stmt = select(UserPermissions).where(
        UserPermissions.subdomain == subdomain,
        UserPermissions.manager_id == manager_id
    )

    result = await session.execute(stmt)
    permissions = result.scalar_one_or_none()

    if permissions:
        logger.info(
            "Настройки найдены в БД | id: %s, created_at: %s",
            permissions.id,
            permissions.created_at
        )
    else:
        logger.info(
            "Настройки не найдены в БД | subdomain: %s, manager_id: %s",
            subdomain,
            manager_id
        )

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
    logger.info(
        "Начало сохранения настроек | subdomain: %s, manager_id: %s",
        request.subdomain,
        request.manager_id
    )

    # Удаляем старые настройки, если они есть
    deleted = await delete_permissions(
        subdomain=request.subdomain,
        manager_id=request.manager_id,
        session=session
    )

    if deleted:
        logger.info(
            "Старые настройки удалены перед сохранением | subdomain: %s, manager_id: %s",
            request.subdomain,
            request.manager_id
        )

    # Создаём новую запись
    permissions_dict = request.permissions.model_dump()

    logger.info(
        "Создание новой записи | permissions_keys: %s",
        list(permissions_dict.keys())
    )

    new_permissions = UserPermissions(
        subdomain=request.subdomain,
        manager_id=request.manager_id,
        permissions=permissions_dict
    )

    session.add(new_permissions)
    await session.commit()
    await session.refresh(new_permissions)

    logger.info(
        "Настройки успешно сохранены в БД | id: %s, created_at: %s",
        new_permissions.id,
        new_permissions.created_at
    )

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
    logger.info(
        "Запрос на удаление настроек из БД | subdomain: %s, manager_id: %s",
        subdomain,
        manager_id
    )

    stmt = delete(UserPermissions).where(
        UserPermissions.subdomain == subdomain,
        UserPermissions.manager_id == manager_id
    )

    result = await session.execute(stmt)
    await session.commit()

    deleted = result.rowcount > 0

    if deleted:
        logger.info(
            "Настройки удалены из БД | rows_deleted: %s",
            result.rowcount
        )
    else:
        logger.info(
            "Записей для удаления не найдено | subdomain: %s, manager_id: %s",
            subdomain,
            manager_id
        )

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
