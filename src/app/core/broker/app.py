"""
Конфигурация FastStream RabbitMQ брокера.
"""

from faststream.rabbit import RabbitBroker, Channel

from app.core.settings import config
from app.core.logging import logger
from app.core.broker.middlewares.logging_middleware import LoggingMiddleware
from app.core.broker.middlewares.retry_middleware import RetryMiddleware
from app.core.broker.routers.permissions import permissions_router
from app.core.broker.routers.health import health_router


# Создаем RabbitMQ брокер с настройками
broker = RabbitBroker(
    url=config.rabbit_cfg.rabbitmq_uri,
    logger=logger,
    middlewares=[
        RetryMiddleware,  # Сначала retry (внешний слой)
        LoggingMiddleware,  # Потом logging (внутренний слой)
    ],
    default_channel=Channel(prefetch_count=config.worker_cfg.PREFETCH_COUNT),
)

# Подключаем роутеры
broker.include_router(permissions_router)
broker.include_router(health_router)
