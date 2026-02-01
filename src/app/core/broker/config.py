"""
Конфигурация RabbitMQ очередей для hiding-data виджета
"""


class QueueNames:
    """Названия очередей RabbitMQ"""
    # Операции с настройками permissions
    SETTINGS_SAVE = "hiding_data_settings_save"
    SETTINGS_GET = "hiding_data_settings_get"
    SETTINGS_DELETE = "hiding_data_settings_delete"

    # Healthcheck
    HEALTH = "hiding_data_health"


# Таймауты и retry настройки
RPC_TIMEOUT = 30  # секунд
MAX_RETRY_COUNT = 3
RETRY_DELAY = 5  # секунд
