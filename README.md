# hiding-data - Виджет сокрытия данных для amoCRM

Backend-сервис для гибкого ограничения видимости данных в amoCRM для конкретных пользователей.

## Описание

Инструмент для администратора amoCRM, позволяющий ограничивать видимость:
- Разделов меню
- Воронок (pipelines)
- Этапов воронок
- Полей (кастомных и стандартных)
- Сделок/контактов/компаний на основе тегов

## Архитектура

- **Backend**: FastAPI + PostgreSQL + RabbitMQ
- **Хранение**: Настройки сохраняются в JSON формате в PostgreSQL
- **Режимы**: Blacklist (скрыть указанное) и Whitelist (скрыть всё, кроме указанного)

## Структура настроек

```json
{
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
      }
    }
  }
}
```

## API Endpoints

### POST /api/settings
Сохранение настроек для менеджера (если существуют - перезаписывает)

**Request:**
```json
{
  "subdomain": "example",
  "manager_id": 12345,
  "permissions": { ... }
}
```

### GET /api/settings/{subdomain}?manager_id=12345
Получение настроек для менеджера

**Response:**
```json
{
  "success": true,
  "data": {
    "subdomain": "example",
    "manager_id": 12345,
    "permissions": { ... },
    "created_at": "2025-01-29T14:30:00",
    "updated_at": "2025-01-29T14:30:00"
  }
}
```

### DELETE /api/settings/{subdomain}?manager_id=12345
Удаление настроек для менеджера

## Сценарии работы

### Кейс 1: Мария Иванова (Blacklist по тегам)
**Настройка:**
```json
{
  "tags_logic": {
    "leads": {
      "mode": "blacklist",
      "values": ["yandex"]
    }
  }
}
```
**Результат:** Мария видит все сделки, но сделки с тегом "yandex" скрываются.

### Кейс 2: Директолог (Whitelist по тегам)
**Настройка:**
```json
{
  "tags_logic": {
    "leads": {
      "mode": "whitelist",
      "values": ["d1"]
    }
  }
}
```
**Результат:** Директолог видит только сделки с тегом "d1", остальные скрыты.

## Установка и запуск

### Требования
- Python 3.12+
- PostgreSQL
- RabbitMQ

### Локальная разработка

1. Клонировать репозиторий
```bash
git clone <repo-url>
cd hiding-data
```

2. Настроить переменные окружения
```bash
cp .env.example .env
# Отредактировать .env под ваши настройки
```

3. Запустить сервисы
```bash
docker-compose -f docker-compose.dev.vendor.yml up -d
```

### Миграции БД

```bash
cd src
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Разработка

### Структура проекта

```
hiding-data/
├── src/
│   ├── app/
│   │   ├── api/                  # HTTP API endpoints
│   │   ├── core/                 # Ядро приложения
│   │   │   ├── broker/          # RabbitMQ обработчики
│   │   │   ├── settings.py      # Конфигурация
│   │   │   └── logging.py       # Логирование
│   │   ├── db/                  # База данных
│   │   ├── models/              # SQLAlchemy модели
│   │   ├── schemas/             # Pydantic схемы
│   │   ├── services/            # Бизнес-логика
│   │   └── utils/               # Утилиты
│   ├── alembic/                 # Миграции БД
│   └── manage.py                # Команды управления
├── .env                          # Переменные окружения
├── docker-compose.dev.vendor.yml # Docker Compose
└── pyproject.toml               # Зависимости

```

### Технологии

- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM для работы с PostgreSQL
- **FastStream** - RabbitMQ integration
- **Pydantic** - Валидация данных
- **Alembic** - Миграции БД
- **asyncpg** - Асинхронный драйвер PostgreSQL

## Лицензия

MIT
