from typing import Any, Dict, List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PermissionMode(BaseModel):
    """Базовая схема для режима ограничения (blacklist или whitelist)"""
    mode: Literal["blacklist", "whitelist", "none"] = Field(
        description="Режим: blacklist - скрыть указанное, whitelist - скрыть всё кроме указанного, none - не применять"
    )
    values: List[Any] = Field(
        default_factory=list,
        description="Список значений (ID, названия и т.д.)"
    )


class FieldsPermissions(BaseModel):
    """Настройки для ограничения видимости полей"""
    leads: PermissionMode = Field(default_factory=lambda: PermissionMode(mode="none", values=[]))
    contacts: PermissionMode = Field(default_factory=lambda: PermissionMode(mode="none", values=[]))
    companies: PermissionMode = Field(default_factory=lambda: PermissionMode(mode="none", values=[]))


class TagsLogic(BaseModel):
    """Настройки для ограничения на основе тегов"""
    leads: PermissionMode = Field(default_factory=lambda: PermissionMode(mode="none", values=[]))
    contacts: PermissionMode = Field(default_factory=lambda: PermissionMode(mode="none", values=[]))
    companies: PermissionMode = Field(default_factory=lambda: PermissionMode(mode="none", values=[]))


class Permissions(BaseModel):
    """Полная структура настроек permissions"""
    menu: PermissionMode = Field(
        default_factory=lambda: PermissionMode(mode="none", values=[]),
        description="Ограничения по разделам меню"
    )
    pipelines: PermissionMode = Field(
        default_factory=lambda: PermissionMode(mode="none", values=[]),
        description="Ограничения по воронкам (pipeline_id)"
    )
    fields: FieldsPermissions = Field(
        default_factory=FieldsPermissions,
        description="Ограничения по полям"
    )
    tags_logic: TagsLogic = Field(
        default_factory=TagsLogic,
        description="Ограничения на основе тегов сделок/контактов/компаний"
    )


# === API Schemas ===

class SaveSettingsRequest(BaseModel):
    """Запрос на сохранение настроек для менеджера"""
    subdomain: str = Field(..., description="Субдомен amoCRM", min_length=1)
    manager_id: int = Field(..., description="ID менеджера", gt=0)
    permissions: Permissions = Field(..., description="Настройки permissions")

    class Config:
        json_schema_extra = {
            "example": {
                "subdomain": "example",
                "manager_id": 12345,
                "permissions": {
                    "menu": {
                        "mode": "blacklist",
                        "values": ["analytics", "notifications"]
                    },
                    "pipelines": {
                        "mode": "whitelist",
                        "values": [743210]
                    },
                    "fields": {
                        "leads": {
                            "mode": "blacklist",
                            "values": [654321, 654322]
                        },
                        "contacts": {
                            "mode": "none",
                            "values": []
                        },
                        "companies": {
                            "mode": "none",
                            "values": []
                        }
                    },
                    "tags_logic": {
                        "leads": {
                            "mode": "whitelist",
                            "values": ["d1", "utm_yandex"]
                        },
                        "contacts": {
                            "mode": "none",
                            "values": []
                        },
                        "companies": {
                            "mode": "none",
                            "values": []
                        }
                    }
                }
            }
        }


class GetSettingsResponse(BaseModel):
    """Ответ с настройками для менеджера"""
    subdomain: str
    manager_id: int
    permissions: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeleteSettingsRequest(BaseModel):
    """Запрос на удаление настроек"""
    subdomain: str = Field(..., description="Субдомен amoCRM", min_length=1)
    manager_id: int = Field(..., description="ID менеджера", gt=0)


class APIResponse(BaseModel):
    """Стандартный ответ API"""
    success: bool
    data: Optional[Any] = None
