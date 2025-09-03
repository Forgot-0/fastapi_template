
---

# FastAPI Template

## Описание

**FastAPI Template** — это продвинутый шаблон для старта проектов на FastAPI с поддержкой:
- модульной архитектуры,
- dependency injection (Dishka),
- асинхронных очередей (Taskiq + Redis),
- аутентификации и авторизации,
- отправки почты,
- rate limiting,
- миграций (Alembic),
- логирования (structlog),
- и других best practices для production-ready приложений.


## Возможности

- JWT-аутентификация (access/refresh токены)
- Регистрация, подтверждение email, восстановление пароля
- Ограничение частоты запросов (rate limiting)
- Асинхронные очереди и фоновые задачи (Taskiq, Redis)
- Отправка email через SMTP
- Модульная DI-архитектура (Dishka)
- Логирование в файл и консоль (structlog)
- Миграции БД (Alembic)
- Гибкая конфигурация через переменные окружения
- Docker/Docker Compose для локального и production запуска


## Конфигурация

Все параметры настраиваются через переменные окружения (см. `.env.example`):

- `ENVIRONMENT` — local/production/testing
- `POSTGRES_*` — параметры подключения к БД
- `REDIS_*` — параметры подключения к Redis
- `SECRET_KEY` — секрет для JWT
- `SMTP_*` — параметры SMTP для отправки почты
- `QUEUE_REDIS_BROKER_URL`, `QUEUE_REDIS_RESULT_BACKEND` — для очередей
- `LOG_LEVEL`, `JSON_LOG`, `PATH_LOG` — логирование


## Аутентификация и авторизация

- JWT (access/refresh)
- Хэширование паролей (bcrypt)
- Подтверждение email
- Восстановление пароля
- Rate limiting на sensitive endpoints
- OAuth2PasswordBearer для защищённых роутов


## Очереди и фоновые задачи

- Используется Taskiq + Redis
- Для запуска воркера:
  ```bash
  docker-compose run queue_worker
  ```
- Пример фоновой задачи: отправка email


## Почта

- Отправка писем через SMTP (aiosmtplib)
- Шаблоны писем на Jinja2
- Email для подтверждения регистрации, восстановления пароля и др.


## Логирование

- structlog (поддержка JSON-логов)
- Логи пишутся в файл и/или консоль
- Уровень логирования настраивается через переменные окружения

## Тестирование
TODO

## TODO и планы на развитие

- Добавить RBAC и роли пользователей
- Добавить интеграцию с внешними OAuth-провайдерами
- Улучшить покрытие тестами
- Добавить healthcheck endpoint
- Улучшить шаблоны email
- Добавить мониторинг и алерты


## Контакты

Автор: Forgot-0  
Telegram: [@Forgot011](https://t.me/Forgot011)

Если у вас есть вопросы или предложения — создавайте issue или pull request!


