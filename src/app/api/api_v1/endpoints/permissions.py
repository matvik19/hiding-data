import json
from fastapi import APIRouter, Query, HTTPException, status
from typing import Dict, Any
from app.schemas.permissions import (
    SaveSettingsRequest,
    GetSettingsResponse,
    DeleteSettingsRequest,
    APIResponse,
)
from app.core.broker.app import broker
from app.core.broker.config import QueueNames, RPC_TIMEOUT

router = APIRouter()


@router.post("/settings", response_model=APIResponse)
async def save_settings(request: SaveSettingsRequest) -> Dict[str, Any]:
    """
    Сохранение настроек permissions для менеджера.
    Если настройки уже существуют - удаляет старые и создаёт новые.
    """
    try:
        response_msg = await broker.request(
            request.model_dump(),
            queue=QueueNames.SETTINGS_SAVE,
            timeout=RPC_TIMEOUT,
        )

        # Десериализация ответа из RabbitMessage
        response = json.loads(response_msg.body)

        if not response or not response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.get("error", "Failed to save settings")
            )

        return {
            "success": True,
            "data": response.get("data")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/settings/{subdomain}", response_model=APIResponse)
async def get_settings(
    subdomain: str,
    manager_id: int = Query(..., description="ID менеджера", gt=0)
) -> Dict[str, Any]:
    """
    Получение настроек permissions для менеджера
    """
    try:
        request_data = {
            "subdomain": subdomain,
            "manager_id": manager_id
        }

        response_msg = await broker.request(
            request_data,
            queue=QueueNames.SETTINGS_GET,
            timeout=RPC_TIMEOUT,
        )

        # Десериализация ответа из RabbitMessage
        response = json.loads(response_msg.body)

        if not response or not response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.get("error", "Settings not found")
            )

        return {
            "success": True,
            "data": response.get("data")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/settings/{subdomain}", response_model=APIResponse)
async def delete_settings(
    subdomain: str,
    manager_id: int = Query(..., description="ID менеджера", gt=0)
) -> Dict[str, Any]:
    """
    Удаление настроек permissions для менеджера
    """
    try:
        request_data = {
            "subdomain": subdomain,
            "manager_id": manager_id
        }

        response_msg = await broker.request(
            request_data,
            queue=QueueNames.SETTINGS_DELETE,
            timeout=RPC_TIMEOUT,
        )

        # Десериализация ответа из RabbitMessage
        response = json.loads(response_msg.body)

        if not response or not response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.get("error", "Failed to delete settings")
            )

        return {
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
