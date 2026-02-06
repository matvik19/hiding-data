from typing import Dict, Any, Annotated
from faststream import Depends
from faststream.rabbit import RabbitQueue, RabbitRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.broker.config import QueueNames
from app.core.broker.dependencies import get_db_session
from app.core.logging import logger, subdomain_var
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
        subdomain_var.set(request.subdomain)

        logger.info(
            "Получено сообщение SAVE | subdomain: %s, manager_id: %s, queue: %s",
            request.subdomain,
            request.manager_id,
            QueueNames.SETTINGS_SAVE
        )

        # Вызов сервисного слоя
        permissions = await save_permissions(request, db_session)

        logger.info(
            "Отправка успешного ответа | subdomain: %s, manager_id: %s, record_id: %s",
            permissions.subdomain,
            permissions.manager_id,
            permissions.id
        )

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
        logger.error(
            "Ошибка обработки SAVE | error: %s, error_type: %s",
            str(e),
            type(e).__name__
        )
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
            logger.warning(
                "Некорректный запрос GET | missing_params: subdomain=%s, manager_id=%s",
                subdomain is None,
                manager_id is None
            )
            return {
                "success": False,
                "error": "subdomain and manager_id are required"
            }

        # Устанавливаем subdomain для логов
        subdomain_var.set(subdomain)

        logger.info(
            "Получено сообщение GET | subdomain: %s, manager_id: %s, queue: %s",
            subdomain,
            manager_id,
            QueueNames.SETTINGS_GET
        )

        # Получение настроек
        permissions = await get_permissions_by_manager(
            subdomain=subdomain,
            manager_id=manager_id,
            session=db_session
        )

        if not permissions:
            logger.info(
                "Отправка ответа NOT_FOUND | subdomain: %s, manager_id: %s",
                subdomain,
                manager_id
            )
            return {
                "success": False,
                "error": "Settings not found"
            }

        logger.info(
            "Отправка успешного ответа GET | subdomain: %s, manager_id: %s, record_id: %s",
            subdomain,
            manager_id,
            permissions.id
        )

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
        logger.error(
            "Ошибка обработки GET | error: %s, error_type: %s",
            str(e),
            type(e).__name__
        )
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
            logger.warning(
                "Некорректный запрос DELETE | missing_params: subdomain=%s, manager_id=%s",
                subdomain is None,
                manager_id is None
            )
            return {
                "success": False,
                "error": "subdomain and manager_id are required"
            }

        # Устанавливаем subdomain для логов
        subdomain_var.set(subdomain)

        logger.info(
            "Получено сообщение DELETE | subdomain: %s, manager_id: %s, queue: %s",
            subdomain,
            manager_id,
            QueueNames.SETTINGS_DELETE
        )

        # Удаление настроек
        deleted = await delete_permissions(
            subdomain=subdomain,
            manager_id=manager_id,
            session=db_session
        )

        if not deleted:
            logger.info(
                "Отправка ответа NOT_FOUND | subdomain: %s, manager_id: %s",
                subdomain,
                manager_id
            )
            return {
                "success": False,
                "error": "Settings not found or already deleted"
            }

        logger.info(
            "Отправка успешного ответа DELETE | subdomain: %s, manager_id: %s",
            subdomain,
            manager_id
        )

        return {
            "success": True
        }
    except Exception as e:
        logger.error(
            "Ошибка обработки DELETE | error: %s, error_type: %s",
            str(e),
            type(e).__name__
        )
        return {
            "success": False,
            "error": str(e)
        }
