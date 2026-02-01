from typing import Dict, Any, Annotated
from faststream import Depends
from faststream.rabbit import RabbitQueue, RabbitRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.broker.config import QueueNames
from app.core.broker.dependencies import get_db_session
from app.services.permissions_service import (
    get_permissions_by_manager,
    save_permissions,
    delete_permissions,
)
from app.schemas.permissions import SaveSettingsRequest

permissions_router = RabbitRouter()


@permissions_router.subscriber(
    RabbitQueue(QueueNames.SETTINGS_SAVE, durable=True)
)
async def handle_save_settings(
    data: dict,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Dict[str, Any]:
    """
    Handler для сохранения настроек permissions.
    Если настройки уже существуют - удаляет старые и создаёт новые.
    """
    try:
        # Валидация данных через Pydantic
        request = SaveSettingsRequest(**data)

        # Сохранение настроек
        permissions = await save_permissions(request, db_session)

        return {
            "success": True,
            "data": {
                "subdomain": permissions.subdomain,
                "manager_id": permissions.manager_id,
                "permissions": permissions.permissions,
                "created_at": permissions.created_at.isoformat() if permissions.created_at else None,
                "updated_at": permissions.updated_at.isoformat() if permissions.updated_at else None,
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@permissions_router.subscriber(
    RabbitQueue(QueueNames.SETTINGS_GET, durable=True)
)
async def handle_get_settings(
    data: dict,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Dict[str, Any]:
    """
    Handler для получения настроек permissions для менеджера
    """
    try:
        subdomain = data.get("subdomain")
        manager_id = data.get("manager_id")

        if not subdomain or not manager_id:
            return {
                "success": False,
                "error": "subdomain and manager_id are required"
            }

        # Получение настроек
        permissions = await get_permissions_by_manager(
            subdomain=subdomain,
            manager_id=manager_id,
            session=db_session
        )

        if not permissions:
            return {
                "success": False,
                "error": "Settings not found"
            }

        return {
            "success": True,
            "data": {
                "subdomain": permissions.subdomain,
                "manager_id": permissions.manager_id,
                "permissions": permissions.permissions,
                "created_at": permissions.created_at.isoformat() if permissions.created_at else None,
                "updated_at": permissions.updated_at.isoformat() if permissions.updated_at else None,
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@permissions_router.subscriber(
    RabbitQueue(QueueNames.SETTINGS_DELETE, durable=True)
)
async def handle_delete_settings(
    data: dict,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Dict[str, Any]:
    """
    Handler для удаления настроек permissions для менеджера
    """
    try:
        subdomain = data.get("subdomain")
        manager_id = data.get("manager_id")

        if not subdomain or not manager_id:
            return {
                "success": False,
                "error": "subdomain and manager_id are required"
            }

        # Удаление настроек
        deleted = await delete_permissions(
            subdomain=subdomain,
            manager_id=manager_id,
            session=db_session
        )

        if not deleted:
            return {
                "success": False,
                "error": "Settings not found or already deleted"
            }

        return {
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
