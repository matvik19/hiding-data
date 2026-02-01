from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, event as sa_event
from app.db.base_class import Base


class UserPermissions(Base):
    """
    Модель для хранения настроек видимости данных для пользователей AmoCRM
    """
    __tablename__ = "user_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subdomain: Mapped[str] = mapped_column(index=True, nullable=False)
    manager_id: Mapped[int] = mapped_column(index=True, nullable=False)

    # JSON структура с настройками permissions
    # Пример: {"menu": {"mode": "blacklist", "values": [...]}, "pipelines": {...}, ...}
    permissions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<UserPermissions(subdomain={self.subdomain}, manager_id={self.manager_id})>"


@sa_event.listens_for(UserPermissions, "before_insert")
def set_created_updated_permissions(mapper, connection, target):
    """Автоматически устанавливает created_at и updated_at при создании записи"""
    now = datetime.now()
    target.created_at = now
    target.updated_at = now


@sa_event.listens_for(UserPermissions, "before_update")
def set_updated_permissions(mapper, connection, target):
    """Автоматически обновляет updated_at при изменении записи"""
    target.updated_at = datetime.now()
