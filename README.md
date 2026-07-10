# FastAPI Template

Production-ready модульный монолит на FastAPI: асинхронный SQLAlchemy 2.0, CQRS-style команды/запросы через собственный медиатор, Dependency Injection на [Dishka](https://github.com/reagento/dishka), событийная модель, готовые сервисы (кэш, очереди, почта, S3-хранилище, WebSocket, Kafka/Redis message-брокеры) и полный набор наблюдаемости (Prometheus, Grafana, Loki).

Вдохновлён [Starter Kit](https://github.com/arctikant/fastapi-modular-monolith-starter-kit).

Модуль `app/auth` — это не просто аутентификация, а **эталонный (reference) модуль**: он показывает, как должен быть устроен любой новый модуль в проекте (модели, фильтры, репозитории, команды/запросы, DI-провайдер, роуты). При добавлении нового функционала — копируйте паттерны оттуда.

## Технологический стек

| Категория | Технологии |
|---|---|
| Web-фреймворк | [FastAPI](https://fastapi.tiangolo.com) 0.135+, Python 3.14, [uvicorn](https://www.uvicorn.org)/[gunicorn](https://gunicorn.org) |
| БД / ORM | [PostgreSQL](https://www.postgresql.org), [SQLAlchemy](https://www.sqlalchemy.org) 2.0 (async, asyncpg), [Alembic](https://github.com/sqlalchemy/alembic) |
| DI | [Dishka](https://github.com/reagento/dishka) |
| Кэш / Rate-limit | Redis, [aiocache](https://github.com/aio-libs/aiocache), [fastapi-limiter](https://github.com/long2ice/fastapi-limiter) |
| Очереди задач | [Taskiq](https://taskiq-python.github.io) + taskiq-redis (worker + scheduler) |
| Message broker | Kafka ([aiokafka](https://github.com/aio-libs/aiokafka)) / Redis Pub-Sub |
| Хранилище файлов | [MinIO](https://min.io) (S3-совместимое) |
| Почта | [aiosmtplib](https://aiosmtplib.readthedocs.io/en/stable) + Jinja2-шаблоны |
| Аутентификация | JWT ([pyjwt](https://pyjwt.readthedocs.io)), Argon2 ([argon2-cffi](https://argon2-cffi.readthedocs.io)), OAuth2 (Google, Yandex, GitHub), RBAC |
| Логирование | [structlog](https://www.structlog.org/en/stable) |
| Мониторинг | Prometheus, Grafana, Loki, Vector |
| Тесты | pytest, pytest-asyncio, [testcontainers](https://testcontainers-python.readthedocs.io) (Postgres, Redis) |
| Линтеры / типы | ruff, mypy, pylint, pre-commit |
| Инфраструктура | Docker / Docker Compose |

## Быстрый старт

```bash
git clone https://github.com/Forgot-0/fastapi_template.git
cd fastapi_template

# 1. Переменные окружения
cp .env.example .env
# отредактируйте .env: минимум SECRET_KEY, JWT_SECRET_KEY, POSTGRES_*

# 2. Docker-сеть (используется всеми docker-compose файлами проекта)
docker network create app-network

# 3. Поднять инфраструктуру и приложение
docker compose up --build
```

После запуска:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- OpenAPI JSON: <http://localhost:8000/api/v1/openapi.json> (доступен только в `local`/`testing` окружениях)
- Health-check: `GET /health`
- Метрики Prometheus: `GET /metrics`
- MinIO Console: <http://localhost:9001>

### Линтинг и типы

```bash
poetry run ruff check .
poetry run mypy .
poetry run pylint app
pre-commit run --all-files
```

---

## Правила для AI-ассистентов

> Этот раздел — инструкция для LLM/AI-агентов (Claude, Copilot, Cursor и т.п.), которые будут писать код в этом репозитории. Следуйте ей так же строго, как и человек-разработчик.

1. **Не изобретайте новую архитектуру.** Проект уже задаёт паттерн: Router → Command/Query → Handler → Repository → Model. Любой новый функционал раскладывается по этим слоям, а не пишется «в одну функцию во вьюхе».
2. **Модуль `app/auth` — эталон.** Перед созданием нового модуля откройте соответствующие файлы `app/auth/*` и повторяйте структуру 1:1 (см. раздел [«Создание нового модуля»](#создание-нового-модуля)).
3. **DI только через Dishka.** Никаких глобальных синглтонов или `Depends()` с ручным созданием сервисов внутри роутера — сервисы и репозитории объявляются в `providers.py` и получаются через `FromDishka[...]`.
4. **Команды меняют состояние, запросы — только читают.** Используйте `BaseCommand`/`BaseCommandHandler` для записи и `BaseQuery`/`BaseQueryHandler` для чтения; не смешивайте побочные эффекты в query-хендлерах.
5. **Фильтрация и пагинация — через `app.core.filters`.** Не пишите вручную `WHERE`/`LIMIT/OFFSET` в репозиториях — создавайте `XxxFilter(BaseFilter)` и используйте `find_by_filter`.
6. **Доступ — через политики (`policies/`), а не проверки внутри бизнес-логики.** RBAC-проверки оформляются как FastAPI-зависимости (`Depends(can_update)`), а не `if user.role == ...` внутри хендлера.
7. **Модели наследуют `BaseModel` (+ миксины).** Новая модель обязательно регистрируется в `app/core/models.py`, иначе Alembic её не увидит.
8. **Придерживайтесь соглашений по именованию** из раздела [«Соглашения по именованию»](#3-соглашения-по-именованию) (`CreateArticle`, `GetListArticles`, `ArticleFilter`, `ArticleRepository` и т.д.).
9. **Каждое изменение бизнес-логики сопровождается тестом** в `tests/` (unit — без БД/Docker, integration — с `testcontainers`, по аналогии с `tests/auth`).
10. **Код обязан проходить `ruff`, `mypy` и `pylint`** — используйте существующие конфиги (`.ruff.toml`, `mypy.ini`, `.pylintrc`), не отключайте правила без крайней необходимости.
11. **Не добавляйте новые зависимости/сервисы «по умолчанию».** Если задачу можно решить существующими сервисами (`CacheServiceInterface`, `QueueServiceInterface`, `StorageService`, `BaseMailService`, `BaseMessageBroker`) — используйте их, а не новую библиотеку.
12. **Секреты и конфигурация — только через `.env` / `BaseConfig`.** Не хардкодьте ключи, хосты или пароли в коде.

---

## Содержание

- [FastAPI Template](#fastapi-template)
  - [Технологический стек](#технологический-стек)
  - [Быстрый старт](#быстрый-старт)
    - [Линтинг и типы](#линтинг-и-типы)
  - [Правила для AI-ассистентов](#правила-для-ai-ассистентов)
  - [Содержание](#содержание)
  - [Введение](#введение)
    - [Project Structure](#project-structure)
    - [Database Layer](#database-layer)
    - [API Layer](#api-layer)
    - [Config](#config)
    - [Dependency Injection](#dependency-injection)
  - [Security](#security)
    - [Policies](#policies)
    - [RBAC внутри Query/Command-хендлеров](#rbac-внутри-querycommand-хендлеров)
    - [OAuth Authentication](#oauth-authentication)
  - [Filter System](#filter-system)
  - [Core Services](#core-services)
    - [Events](#events)
    - [Cache Service](#cache-service)
    - [Queue Service](#queue-service)
    - [Mail Service](#mail-service)
    - [Storage Service](#storage-service)
    - [WebSocket Service](#websocket-service)
    - [Message Brokers](#message-brokers)
    - [Logging Service](#logging-service)
    - [Monitoring](#monitoring)
    - [Middleware](#middleware)
  - [Application Lifecycle](#application-lifecycle)
    - [Startup Sequence](#startup-sequence)
    - [Shutdown](#shutdown)
  - [Создание нового модуля](#создание-нового-модуля)
    - [1. Структура модуля](#1-структура-модуля)
    - [2. Пошаговое создание](#2-пошаговое-создание)
    - [3. Соглашения по именованию](#3-соглашения-по-именованию)

---

## Введение

### Project Structure

```
fastapi_template/
├── migrations/          # Alembic migrations
├── app/                 # Application package
│   ├── main.py          # Application entry point
│   ├── pre_start.py     # Pre-start DB checks
│   ├── init_data.py     # Initial data setup (roles, permissions)
│   ├── tasks.py         # Taskiq worker entry point & scheduler
│   ├── core/            # Core functionality
│   │   ├── api/         # API utilities (builder, rate_limiter, schemas, filter_mapper)
│   │   ├── configs/     # Configuration management
│   │   ├── db/          # Database utilities (base_model, repository, session, convertor)
│   │   ├── di/          # Dependency injection container & providers
│   │   ├── events/      # Event system (event, service, mediator)
│   │   ├── filters/     # Generic filter system (base, condition, sort, pagination, loading_strategy)
│   │   ├── log/         # Logging configuration (structlog)
│   │   ├── mediators/   # Mediator pattern (command & query registries)
│   │   ├── message_brokers/  # Kafka / Redis pub-sub
│   │   ├── middlewares/      # ContextMiddleware, LoggingMiddleware
│   │   ├── models.py    # Central import of all ORM models (for Alembic)
│   │   ├── routers.py   # Health-check endpoint
│   │   ├── services/    # Core services (auth, cache, mail, queues, storage)
│   │   └── websockets/  # WebSocket connection manager
│   └── auth/            # Auth module (example module structure)
│       ├── commands/    # Command handlers (auth, permissions, roles, sessions, users)
│       ├── dtos/        # Internal data-transfer objects
│       ├── emails/      # Email templates & HTML views
│       ├── events/      # Module-specific event handlers
│       ├── filters/     # Auth-specific filter classes (UserFilter, RoleFilter, …)
│       ├── models/      # ORM models (User, Role, Permission, Session, OAuthAccount)
│       ├── queries/     # Query handlers (auth, permissions, roles, sessions, users)
│       ├── repositories/  # Data access layer (SQLAlchemy + Redis)
│       ├── routes/      # API routes (v1: auth, users, roles, permissions, sessions)
│       ├── schemas/     # Pydantic request / response schemas
│       ├── services/    # Business-logic services (JWT, OAuth, RBAC, hash, session, cookie)
│       ├── config.py    # Auth module config
│       ├── deps.py      # FastAPI dependencies (CurrentUser, ActiveUser, …)
│       ├── exceptions.py
│       ├── gateway.py   # BaseAuthGateway interface
│       ├── providers.py # Dishka DI provider
│       ├── routers.py   # Top-level router
│       └── tasks.py     # Taskiq task registration
├── monitoring/          # Grafana / Loki / Vector config
└── pyproject.toml
```

---

### Database Layer

**Используется:**

- Database: [PostgreSQL](https://www.postgresql.org)
- Async adapter: [asyncpg](https://pypi.org/project/asyncpg/)
- ORM: [SQLAlchemy](https://www.sqlalchemy.org) 2.0+ (async)
- Migrations: [Alembic](https://github.com/sqlalchemy/alembic)

**Key Notes:**

- `app.core.db.BaseModel` — базовый класс для всех моделей, наследует `sqlalchemy.orm.DeclarativeBase`. Реализует `from_dict()`, `update()`, а также систему событий (`register_event()` / `pull_events()`).
- `app.core.db.DateMixin` — добавляет поля `created_at` и `updated_at`.
- `app.core.db.SoftDeleteMixin` — «мягкое» удаление через поле `deleted_at`. Предоставляет `select_not_deleted()` classmethod и `soft_delete()` / `is_deleted()`.
- Все модели должны быть импортированы в `app/core/models.py`, чтобы Alembic их видел.

```python
from app.core.db.base_model import BaseModel, DateMixin, SoftDeleteMixin

class Post(BaseModel, DateMixin, SoftDeleteMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
```

---

### API Layer

**Используется:**

- Rate limiting: [fastapi-limiter](https://github.com/long2ice/fastapi-limiter) + Redis
- Metrics: [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)

**Структура эндпоинтов и схем**

Каждый модуль организован следующим образом:

- `routes/v<N>/<entity>.py` — роутеры FastAPI
- `schemas/<entity>/requests.py` — входящие Pydantic-схемы с методом `to_<entity>_filter() -> Filter`
- `schemas/<entity>/responses.py` — исходящие схемы

Пример схемы запроса со встроенной конвертацией в фильтр:

```python
class GetUsersRequest(BaseModel):
    email: str | None = None
    is_active: bool | None = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort: str | None = Field(default=None, examples=["created_at:desc,username:asc"])

    def to_user_filter(self) -> UserFilter:
        user_filter = UserFilter(email=self.email, is_active=self.is_active)
        user_filter.set_pagination(Pagination(page=self.page, page_size=self.page_size))
        for sf in FilterMapper.parse_sort_string(self.sort):
            user_filter.add_sort(sf.field, sf.direction)
        return user_filter
```

Использование в роутере:

```python
@router.get("/")
async def get_list(
    mediator: FromDishka[BaseMediator],
    user_jwt_data: AuthCurrentUserJWTData,
    params: GetUsersRequest = Query(),
) -> PageResult[UserDTO]:
    return await mediator.handle_query(
        GetListUserQuery(user_jwt_data=user_jwt_data, user_filter=params.to_user_filter())
    )
```

**Rate Limiter**

`app.core.api.rate_limiter.ConfigurableRateLimiter` — обёртка над `RateLimiter` из `fastapi-limiter`:

```python
from app.core.api.rate_limiter import ConfigurableRateLimiter

router = APIRouter(dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60))])

# или на конкретном эндпоинте:
@app.get("/", dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60))])
async def index(): ...
```

**Формирование ответов об ошибках**

`app.core.api.builder.create_response` генерирует OpenAPI-совместимое описание ошибки:

```python
@router.post(
    "/login",
    responses={400: create_response(WrongLoginDataException(username="user"))}
)
async def login(...): ...
```

---

### Config

**Key Notes:**

- Глобальный конфиг: `app.core.configs.app_config` (класс `AppConfig`).
- Каждый модуль может иметь собственный `config.py`, унаследованный от `app.core.configs.BaseConfig`.
- Все настройки читаются из файла `.env`.
- `.env.example` — шаблон всех переменных; скопируйте его в `.env` при первом развёртывании.

---

### Dependency Injection

Используется фреймворк [Dishka](https://github.com/reagento/dishka).

**Container Setup:**

```python
# app/core/di/container.py
from dishka import AsyncContainer, make_async_container
from app.auth.providers import AuthModuleProvider
from app.core.di import get_core_providers

def create_container(*app_providers) -> AsyncContainer:
    return make_async_container(
        *get_core_providers(),
        AuthModuleProvider(),
        *app_providers
    )
```

**Инициализация с FastAPI:**

```python
from dishka.integrations.fastapi import setup_dishka
from app.core.di.container import create_container

app = FastAPI(lifespan=lifespan)
container = create_container()
setup_dishka(container=container, app=app)
```

**Использование в эндпоинтах:**

```python
from dishka import FromDishka
from app.core.mediators.base import BaseMediator

@router.get("/")
async def example(mediator: FromDishka[BaseMediator]):
    result = await mediator.handle_query(SomeQuery(...))
    return result
```

**Lifetime scopes:** `APP`, `REQUEST` and more.

---

## Security

### Policies

Логика доступа выносится в отдельные функции-политики в директории `policies/` модуля:

```python
# app/our_module/policies/posts.py
from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import AccessDeniedException

async def can_update(user: AuthUserJWTData) -> bool:
    if "post:update" not in user.permissions:
        raise AccessDeniedException(need_permissions={"post:update"})
    return True
```

Использование в роутере:

```python
@router.patch("/{post_id}", dependencies=[Depends(can_update)])
async def update(post_id: int) -> None: ...
```

### RBAC внутри Query/Command-хендлеров

`Policies` выше проверяют права ещё до входа в хендлер (на уровне FastAPI-зависимости). Но там, где решение о доступе зависит от данных самого запроса (например, `AuthUserJWTData` уже приехал внутрь `Query`/`Command`, а не отдельным параметром роута), проверку делают прямо в `handle()` через RBAC-менеджер — как в [`GetListUserQueryHandler`](#2-пошаговое-создание).

**Порт и адаптер, а не два независимых менеджера.** Это модульный монолит: модуль `app/auth` может быть в будущем полностью удалён и заменён, например, клиентом к внешнему auth-микросервису. Чтобы core и другие модули не зависели от того, как именно `app/auth` считает роли/права, RBAC оформлен как классический port/adapter (инверсия зависимостей):

- **`app.core.services.auth.rbac.RBACManagerInterface`** (core) — абстрактный контракт (`ABC`), знает только про базовый `UserJWTData`. Core и любой другой модуль зависят **только** от этого интерфейса (`FromDishka[RBACManagerInterface]`) и никогда не импортируют `app.auth` напрямую.
- **`app.auth.services.rbac.AuthRBACManager`** (модуль `app/auth`) — конкретная реализация (`AuthRBACManager(RBACManagerInterface)`), которая уже знает про `RolesEnum`/`PermissionEnum` и добавляет модуль-специфичные проверки.
- Связывает их DI: `AuthModuleProvider` регистрирует `AuthRBACManager` как обычный сервис и дополнительно объявляет `alias(source=AuthRBACManager, provides=RBACManagerInterface)` — тот же singleton доступен под двумя типами. Замена auth-модуля на внешний сервис = замена одного `alias`/провайдера в одном месте, без единой правки в core или в других модулях.

| | `RBACManagerInterface` (порт, `app/core`) | `AuthRBACManager` (адаптер, `app/auth`) |
|---|---|---|
| Роль | Контракт: что core вправе ожидать от RBAC, не зная деталей | Единственная реализация контракта сейчас |
| `check_permission(jwt_data, perms)` | Абстрактный метод контракта | `True`, если пользователь — системная роль (`RolesEnum.SYSTEM_ADMIN`/`SUPER_ADMIN`) либо обладает всеми `perms`; пустой `perms` — всегда `True` |
| `is_system_user(jwt_data)` | Абстрактный метод контракта | Роли берутся из `RolesEnum`, а не хардкодятся строками |
| `validate_role_name(jwt_data, name)` | — (не часть общего контракта, модуль-специфично) | Проверяет длину имени роли (3–24 символа) и что системные префиксы (`system_`, `admin_`) создают только системные пользователи |
| `validate_permissions(jwt_data, perm)` | — | Запрещает выдавать/редактировать `protected_permissions` (например, `MANAGE_SYSTEM_SETTINGS`, `ASSIGN_ROLE`) не-системным пользователям |
| `check_security_level(user_level, role_level)` | — | Запрещает управлять ролью с уровнем ≥ уровня самого пользователя (иерархия ролей) |

Модуль-специфичные методы (`validate_role_name`, `validate_permissions`, `check_security_level`) сознательно не вынесены в `RBACManagerInterface` — это детали конкретно ролевой модели `app/auth` (иерархия уровней, защищённые permissions), а не то, что обязано знать/предоставлять любое совместимое хранилище прав. В интерфейс попадает только тот минимум, которым реально пользуется код за пределами `app/auth`.

`AccessDeniedError(need_permissions=...)` (`app.core.services.auth.exceptions`) — единый формат ошибки для всего проекта, конвертируется глобальным exception-хендлером в HTTP 403 с телом `{"code": "ACCESS_DENIED", "detail": {"permissions": [...]}}`.

**Правило:** если хендлеру нужна и пагинация/кэш, и RBAC — проверка прав всегда идёт первой инструкцией в `handle()`, до вызова `cache_paginated`/`cache` (см. объяснение в разборе `GetListUserQueryHandler`).

### OAuth Authentication

**Поддерживаемые провайдеры:** Google, Yandex, GitHub.

**Структура:**

- `OAuthProvider` — абстрактный базовый класс
- `OAuthProviderFactory` — реестр провайдеров, создаётся в `AuthModuleProvider`
- `OAuthManager` — фасад для получения URL авторизации и обработки callback

**API Endpoints:**

| Method | Path | Описание |
|--------|------|----------|
| `GET` | `/api/v1/auth/oauth/{provider}/authorize` | Получить URL авторизации |
| `GET` | `/api/v1/auth/oauth/{provider}/authorize/connect` | Привязать OAuth к существующему аккаунту |
| `GET` | `/api/v1/auth/oauth/{provider}/callback` | Callback от провайдера |

**Конфигурация** (`.env`):

```env
OAUTH_GOOGLE_CLIENT_ID=...
OAUTH_GOOGLE_CLIENT_SECRET=...
OAUTH_GOOGLE_REDIRECT_URI=...
# Аналогично для YANDEX и GITHUB
```

---

## Filter System

Система фильтрации реализована в `app/core/filters/` и обеспечивает типобезопасное построение SQL-запросов через `SQLAlchemyFilterConverter`.

**Компоненты:**

- `BaseFilter` — базовый класс фильтра; хранит условия, сортировку, пагинацию и стратегии загрузки связей.
- `FilterCondition` / `FilterOperator` — одно условие фильтра и доступные операторы.
- `Pagination` — параметры страницы (page, page_size, offset, limit).
- `SortField` / `SortDirection` — параметры сортировки.
- `RelationshipLoading` / `LoadingStrategyType` — eager-loading стратегии (SELECTIN, JOINED, SUBQUERY, LAZY).

**Создание фильтра:**

```python
from dataclasses import dataclass
from app.core.filters.base import BaseFilter
from app.core.filters.condition import FilterOperator
from app.core.filters.loading_strategy import LoadingStrategyType

@dataclass
class PostFilter(BaseFilter):
    title: str | None = None
    is_published: bool | None = None

    def build_condition(self) -> None:
        self.add_condition("title", FilterOperator.CONTAINS, self.title)
        self.add_condition("is_published", FilterOperator.EQ, self.is_published)
        self.add_relation("author", LoadingStrategyType.SELECTIN)
```

**Использование в репозитории:**

```python
# IRepository.find_by_filter() применяет фильтр автоматически
result: PageResult[Post] = await self.post_repository.find_by_filter(
    model=Post,
    filters=PostFilter(title="fastapi", is_published=True)
)
```

**Доступные операторы** (`FilterOperator`):

`EQ`, `NE`, `GT`, `GTE`, `LT`, `LTE`, `IN`, `NOT_IN`, `CONTAINS`, `STARTS_WITH`, `ENDS_WITH`, `IS_NULL`, `IS_NOT_NULL`, `IS_NULL_FROM`, `IS_NOT_NULL_FROM`

**Пагинация и сортировка:**

```python
from app.core.filters.pagination import Pagination
from app.core.filters.sort import SortDirection
from app.core.api.filter_mapper import FilterMapper

post_filter = PostFilter(title="fastapi")
post_filter.set_pagination(Pagination(page=1, page_size=20))
post_filter.add_sort("created_at", SortDirection.DESC)

# Парсинг строки сортировки из query-параметров:
for sf in FilterMapper.parse_sort_string("created_at:desc,title:asc"):
    post_filter.add_sort(sf.field, sf.direction)
```

**`PageResult`** — возвращаемый тип `find_by_filter`:

```python
@dataclass(frozen=True)
class PageResult(Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    # computed: total_pages, has_next, has_previous, next_page, previous_page
```

---

## Core Services

### Events

**Компоненты:**

- `BaseEvent` — базовый класс события (frozen dataclass, обязателен `__event_name__`)
- `BaseEventHandler` — абстрактный обработчик события
- `EventRegisty` — реестр подписок
- `BaseEventBus` / `MediatorEventBus` — шина событий, работающая через Dishka-контейнер

**Создание события:**

```python
from dataclasses import dataclass
from app.core.events.event import BaseEvent

@dataclass(frozen=True)
class PostPublishedEvent(BaseEvent):
    post_id: int
    author_email: str
    __event_name__: str = "posts.post.published"
```

**Создание обработчика:**

```python
@dataclass(frozen=True)
class NotifyAuthorHandler(BaseEventHandler[PostPublishedEvent, None]):
    mail_service: BaseMailService

    async def __call__(self, event: PostPublishedEvent) -> None:
        await self.mail_service.send_plain(
            subject="Ваш пост опубликован",
            recipient=event.author_email,
            body="..."
        )
```

**Публикация из модели:**

```python
class Post(BaseModel):
    @classmethod
    def publish(cls, ...) -> "Post":
        post = Post(...)
        post.register_event(PostPublishedEvent(post_id=post.id, author_email=...))
        return post
```

**В команде:**

```python
await self.session.commit()
await self.event_bus.publish(post.pull_events())
```

**Регистрация в провайдере:**

```python
@decorate
def register_events(self, registry: EventRegisty) -> EventRegisty:
    registry.subscribe(PostPublishedEvent, [NotifyAuthorHandler])
    return registry
```

**Best Practices:**

- Имена событий — прошедшее время (`posts.post.published`, `auth.user.created`, `module.model.action`)
- События неизменяемы (`frozen=True`)
- Один обработчик — один файл: `events/<entity>/<event_name>.py`

---

### Cache Service

**Используется:** [aiocache](https://github.com/aio-libs/aiocache) + Redis

`CacheServiceInterface` доступен через DI:

```python
from dishka import FromDishka
from app.core.services.cache.base import CacheServiceInterface

@router.get("/items/{item_id}")
async def get_item(item_id: int, cache: FromDishka[CacheServiceInterface]):
    cached = await cache.get(f"item:{item_id}")
    if cached:
        return cached
    item = await get_from_db(item_id)
    await cache.set(f"item:{item_id}", item, ttl=60)
    return item

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, cache: FromDishka[CacheServiceInterface]):
    await cache.delete(f"item:{item_id}")
    ...
```

Для кеширования запросов к репозиторию также можно использовать `CacheRepository` (в `app/core/db/repository.py`, подмешивается в каждый `IRepository`, поэтому доступен как `self.<entity>_repository.cache(...)` / `self.<entity>_repository.cache_paginated(...)` прямо в query-хендлере — см. пример [`GetListUserQueryHandler`](#2-пошаговое-создание) выше).

| Метод | Когда использовать |
|---|---|
| `cache(type_model, func, ttl=60, *args, **kwargs)` | Кэширование одного объекта: сам строит ключ по модели/функции/аргументам через `_build_key`. |
| `cache_paginated(type_model, func, ttl=60, *args, **kwargs)` | То же самое, но для `PageResult[...]` (списки с пагинацией) — именно этот метод используется в `GetListUserQueryHandler`. |
| `cache_with_key(key, type_model, func, ttl=60, ...)` / `cache_with_key_paginated(...)` | Те же операции, но с явно заданным ключом — когда нужен предсказуемый/переиспользуемый ключ, а не автогенерируемый хэш. |
| `invalidate_cache(*keys)` | Без аргументов — инкрементирует общую версию списков (мгновенно «протухают» все `cache_paginated`-ключи модели); с ключами — удаляет конкретные записи. Вызывайте после `create/update/delete` в соответствующих командах. |

Во всех случаях `func` — это awaitable-функция без побочных проверок доступа (см. паттерн `handle` / `_handle` в разборе `GetListUserQueryHandler`): она вызывается только при промахе кэша, а её результат (Pydantic-модель или `PageResult` из Pydantic-моделей) сериализуется в Redis через `model_dump_json()`/`orjson`.

---

### Queue Service

**Используется:** [Taskiq](https://taskiq-python.github.io) + [taskiq-redis](https://github.com/taskiq-python/taskiq-redis)

**Создание задачи:**

```python
from dataclasses import dataclass
from app.core.services.queues.task import BaseTask

@dataclass
class ResizeImage(BaseTask):
    __task_name__ = "image.resize"

    @staticmethod
    @inject
    async def run(file_key: str, width: int, storage: FromDishka[StorageService]) -> None:
        ...
```

**Регистрация** в `app/core/tasks.py` → `register_tasks(broker)`.

**Отправка в очередь:**

```python
from app.core.services.queues.service import QueueServiceInterface

await queue_service.push(
    task=ResizeImage,
    data={"file_key": "uploads/photo.jpg", "width": 800},
)
```

В тестовом окружении (`ENVIRONMENT=testing`) используется `InMemoryBroker`.

---

### Mail Service

**Используется:** [aiosmtplib](https://aiosmtplib.readthedocs.io/en/stable) + [Jinja2](https://jinja.palletsprojects.com)

**Создание шаблона:**

```python
from pathlib import Path
from app.core.services.mail.template import BaseTemplate

class WelcomeTemplate(BaseTemplate):
    def __init__(self, username: str) -> None:
        self.username = username

    def _get_dir(self) -> Path:
        return Path("app/my_module/emails/views")

    def _get_name(self) -> str:
        return "welcome.html"
```

HTML-шаблон (`welcome.html`):

```html
<h1>Привет, {{ username }}!</h1>
<p>Добро пожаловать.</p>
```

**Отправка:**

```python
from app.core.services.mail.service import BaseMailService, EmailData

email_data = EmailData(subject="Добро пожаловать", recipient=user.email)
template = WelcomeTemplate(username=user.username)

await mail_service.send(template=template, email_data=email_data)   # синхронно
await mail_service.queue(template=template, email_data=email_data)  # через очередь
```

---

### Storage Service

**Используется:** [MinIO](https://min.io) (S3-compatible) + [minio-py](https://github.com/minio/minio-py)

**Основные методы `StorageService`:**

| Метод | Описание |
|-------|----------|
| `upload_file(UploadFile)` | Загрузить файл, вернуть key или public URL |
| `upload_put_url(bucket, key, expires)` | Presigned PUT URL |
| `upload_post_file(UploadFilePost)` | Presigned POST (browser upload) |
| `generate_presigned_url(bucket, key, expires)` | Presigned GET URL |
| `delete_file(bucket, key)` | Удалить файл |
| `download(bucket, key)` | Скачать как bytes |

```python
from dishka import FromDishka
from app.core.services.storage.service import StorageService
from app.core.services.storage.dtos import UploadFile

@router.post("/upload")
async def upload(file: FastAPIUploadFile, storage: FromDishka[StorageService]):
    key = await storage.upload_file(UploadFile(
        bucket_name="base",
        file_content=file.file,
        file_key=f"uploads/{file.filename}",
        size=file.size,
        content_type=file.content_type,
    ))
    return {"file_key": key}
```

**Bucket Policies** (`app.core.services.storage.aminio.policy.Policy`):

`NONE` (private) | `GET` | `READ` | `WRITE` | `READ_WRITE`

Настраиваются в `CoreProvider`:

```python
@provide(scope=Scope.APP)
def bucket_policy(self) -> dict[str, Policy]:
    return {"base": Policy.NONE, "public": Policy.READ}
```

---

### WebSocket Service

**Компоненты:** `BaseConnectionManager` / `ConnectionManager` (Redis pub-sub для горизонтального масштабирования).

```python
from dishka import FromDishka
from app.core.websockets.base import BaseConnectionManager
from fastapi import WebSocket

@router.websocket("/ws/{room_id}")
async def ws_endpoint(
    websocket: WebSocket,
    room_id: str,
    manager: FromDishka[BaseConnectionManager],
):
    await manager.accept_connection(websocket, key=room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_json_all(key=room_id, data={"message": data})
    except Exception:
        await manager.remove_connection(websocket, key=room_id)
```

**Методы:** `accept_connection`, `remove_connection`, `send_all`, `send_json_all`, `disconnect_all`, `publish` (Redis).

---

### Message Brokers

**Используется:** Kafka ([aiokafka](https://github.com/aio-libs/aiokafka))

Оба реализуют интерфейс `BaseMessageBroker`:

```python
from dishka import FromDishka
from app.core.message_brokers.base import BaseMessageBroker

# Отправка события
await broker.send_event(key="user_123", topic="user_events", event=UserCreatedEvent(...))

# Отправка произвольных данных
await broker.send_data(key="order_1", topic="orders", data={"action": "created"})

# Потребление
async for message in broker.start_consuming(["user_events"]):
    print(message)
```

Брокер автоматически стартует и останавливается в `lifespan` приложения.

---

### Logging Service

**Используется:** [structlog](https://www.structlog.org/en/stable)

Настройка в `app/core/log/init.py` (`configure_logging()`). Поддерживает JSON и console-рендеринг, файловый хендлер, интеграцию с `ContextMiddleware` для добавления `request_id`.

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Something happened", extra={"user_id": 42})
logger.error("Error occurred", exc_info=True)
```

---

### Monitoring

**Prometheus** — метрики экспортируются через `prometheus-fastapi-instrumentator`:

```python
PrometheusFastApiInstrumentator().instrument(app).expose(app, tags=["core"])
# Эндпоинт: GET /metrics
```

**Health check:**

```
GET /health → 200 "Ok"
```

В директории `monitoring/` расположены конфиги Grafana, Loki и Vector.

---

### Middleware

**Встроенные middleware (порядок регистрации → порядок выполнения LIFO):**

| Middleware | Назначение |
|-----------|-----------|
| `ContextMiddleware` | Генерирует `request_id` (UUID), добавляет в `scope["state"]` и заголовок `x-request-id` |
| `GZipMiddleware` | Сжатие ответов ≥ 1000 байт |
| `CORSMiddleware` | Добавляется если задан `BACKEND_CORS_ORIGINS` |
| `LoggingMiddleware` | Логирует метод, путь, статус и время обработки каждого запроса |

Реализованы как ASGI middleware (без `BaseHTTPMiddleware`).

```python
# app/main.py
def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    if app_config.BACKEND_CORS_ORIGINS:
        app.add_middleware(CORSMiddleware, ...)
    app.add_middleware(ContextMiddleware)  # выполняется первым
```

---

## Application Lifecycle

### Startup Sequence

1. **Pre-start** (`pre_start.py`) — проверка подключения к БД с retry (tenacity).
2. **Init data** (`init_data.py`) — создание базовых ролей (`super_admin`, `system_admin`, `user`).
3. **FastAPILimiter** — инициализация Redis-клиента для rate limiting.
4. **Message Broker** — запуск Kafka producer/consumer.

### Shutdown

`lifespan` завершает Redis-клиент, message broker и Dishka-контейнер.

---

## Создание нового модуля

### 1. Структура модуля

```
new_module/
├── models/              # ORM-модели
├── dtos/                # Внутренние DTO (Pydantic)
├── schemas/             # Request / Response схемы
│   └── <entity>/
│       ├── requests.py
│       └── responses.py
├── filters/             # Filter-классы
├── repositories/        # Репозитории (SQLAlchemy + Redis)
├── commands/            # Command + CommandHandler
│   └── <entity>/
├── queries/             # Query + QueryHandler
│   └── <entity>/
├── events/              # EventHandler
│   └── <entity>/
├── emails/              # (опционально) шаблоны писем
│   ├── templates.py
│   └── views/
├── __init__.py
├── config.py            # (опционально) ModuleConfig(BaseConfig)
├── gateway.py           # (опционально) интерфейс для межмодульного доступа
├── exceptions.py
├── deps.py              # FastAPI-зависимости
├── providers.py         # Dishka-провайдер
└── routers.py           # Агрегирующий роутер
```

### 2. Пошаговое создание

**1. Модель:**

```python
from app.core.db.base_model import BaseModel, DateMixin

class Article(BaseModel, DateMixin):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
```

Зарегистрировать в `app/core/models.py`.

**2. Фильтр:**

```python
@dataclass
class ArticleFilter(BaseFilter):
    title: str | None = None

    def build_condition(self) -> None:
        self.add_condition("title", FilterOperator.CONTAINS, self.title)
```

**3. Репозиторий:**

```python
@dataclass
class ArticleRepository(IRepository[Article]):
    async def create(self, article: Article) -> None:
        self.session.add(article)

    def apply_relationship_filters(self, stmt: Select, filters: ArticleFilter) -> Select:
        return stmt
```

**4. Command + Handler:**

```python
@dataclass(frozen=True)
class CreateArticleCommand(BaseCommand):
    title: str
    user_id: int

@dataclass(frozen=True)
class CreateArticleCommandHandler(BaseCommandHandler[CreateArticleCommand, ArticleDTO]):
    session: AsyncSession
    article_repository: ArticleRepository

    async def handle(self, command: CreateArticleCommand) -> ArticleDTO:
        article = Article(title=command.title)
        await self.article_repository.create(article)
        await self.session.commit()
        return ArticleDTO.model_validate(article)
```

**4.1. Query + Handler (пагинация + кэш + RBAC):**

Пока `Command` выше отвечает за запись, `Query` отвечает только за чтение — и часто требует пагинацию, кэширование и проверку прав. Ниже — реальный обработчик из `app/auth/queries/users.py`, разобранный построчно.

```python
from dataclasses import dataclass

from app.auth.dtos.user import AuthUserJWTData, UserDTO
from app.auth.filters.users import UserFilter
from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.db.repository import PageResult
from app.core.queries import BaseQuery, BaseQueryHandler
from app.core.services.auth.exceptions import AccessDeniedError


@dataclass(frozen=True)
class GetListUserQuery(BaseQuery):
    user_filter: UserFilter
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class GetListUserQueryHandler(BaseQueryHandler[GetListUserQuery, PageResult[UserDTO]]):
    user_repository: UserRepository
    rbac_manager: AuthRBACManager

    async def handle(self, query: GetListUserQuery) -> PageResult[UserDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"user:view"}):
            raise AccessDeniedError(need_permissions={"user:view"} - set(query.user_jwt_data.permissions))

        return await self.user_repository.cache_paginated(
            UserDTO, self._handle, ttl=200,
            user_filter=query.user_filter,
        )

    async def _handle(self, user_filter: UserFilter) -> PageResult[UserDTO]:
        pagination_users = await self.user_repository.find_by_filter(
            User,
            filters=user_filter
        )

        return PageResult(
            items=[UserDTO.model_validate(user) for user in pagination_users.items],
            total=pagination_users.total,
            page=pagination_users.page,
            page_size=pagination_users.page_size
        )
```

Разбор по частям:

- **`GetListUserQuery`** — как и любой `BaseQuery`, это неизменяемый (`frozen=True`) dataclass. Он не содержит логики — только данные, необходимые обработчику: уже собранный `UserFilter` (см. [Filter System](#filter-system)) и JWT-данные текущего пользователя `AuthUserJWTData` (нужны для проверки прав внутри хендлера).
- **`GetListUserQueryHandler`** наследует `BaseQueryHandler[GetListUserQuery, PageResult[UserDTO]]` — типизированный контракт «на входе `GetListUserQuery`, на выходе `PageResult[UserDTO]`». Зависимости (`UserRepository`, `AuthRBACManager`) объявлены как обычные поля dataclass и подставляются Dishka через `providers.py` — никакого ручного создания сервисов внутри хендлера.
- **Проверка прав — первым делом в `handle`, до кэша.** `rbac_manager.check_permission(...)` вызывается в публичном `handle`, а не в закэшированном `_handle`. Это важно: если бы проверка была внутри `_handle`, при попадании в кэш (cache hit) она бы вообще не выполнилась, и второй пользователь без нужных прав получил бы чужой закэшированный ответ. При отсутствии прав выбрасывается `AccessDeniedError(need_permissions=...)` — глобальный exception-хендлер сам превратит её в HTTP 403 (см. `app/core/exceptions.py`).
- **Разделение `handle` / `_handle`.** Публичный `handle` = «проверить права → вызвать `cache_paginated`». Приватный `_handle` = «чистая» функция без побочных проверок, которую `cache_paginated` вызывает только при промахе кэша (cache miss) и результат которой сериализуется в Redis. Такое разделение — стандартный паттерн для любого читающего хендлера, где нужен и RBAC, и кэш.
- **В кэш и в `_handle` передаётся только `user_filter`, а не весь `query`.** Это специально: ключ кэша строится из тех же `*args/**kwargs`, что передаются в закэшированную функцию (см. ниже), поэтому в него нельзя передавать `query` целиком — внутри него лежит `user_jwt_data` (роли/права конкретного пользователя). Если бы ключ включал JWT-данные, кэш почти никогда бы не переиспользовался между пользователями (а с учётом того, что `roles`/`permissions` собираются в `set` — ещё и был бы нестабилен между запусками процесса из-за рандомизации хэшей). Правило: в кэшируемую функцию передаются только параметры, которые действительно влияют на *содержимое* ответа; авторизационный контекст туда не попадает — он уже проверен строкой выше.
- **`user_repository.cache_paginated(UserDTO, self._handle, ttl=200, user_filter=query.user_filter)`** — обёртка из `CacheRepository` (`app/core/db/repository.py`, подмешивается в каждый `IRepository`). Она сама строит ключ кэша на основе имени модели DTO, модуля/имени функции (`self._handle`) и хэша переданных аргументов (`user_filter`), проверяет Redis, а при промахе вызывает `self._handle(user_filter=user_filter)`, сохраняет `PageResult` в Redis на `ttl` секунд и возвращает результат. При изменении данных кэш инвалидируется через `invalidate_cache()` (инкремент версии), что делает все ранее выданные ключи для этой модели «протухшими» без явного удаления каждого ключа.
- **`find_by_filter(User, filters=user_filter)`** — общий метод `IRepository` (не специфичный для `User`): строит `SELECT` с учётом `loading_config` фильтра (жадная подгрузка связей), применяет условия из фильтра, считает `COUNT(*)` для `total`, применяет сортировку и `OFFSET/LIMIT` из `filters.pagination`, и возвращает уже готовый `PageResult[User]` — конвертация в DTO происходит уровнем выше, в `_handle`.
- **Маппинг в DTO.** Каждая ORM-модель конвертируется явно: `UserDTO.model_validate(user)`. Хендлеры никогда не возвращают ORM-модели наружу — только DTO/Pydantic-схемы.

**Правило для любого нового кэширующего query-хендлера:** в `cache`/`cache_paginated` передавайте явными kwargs только то подмножество параметров запроса, которое влияет на данные (фильтр, id и т.п.). Никогда не передавайте туда весь `Query`/`Command` целиком, если внутри есть JWT-данные, объект пользователя или что-то ещё, что делает ключ кэша шире, чем реально нужно.

Используйте этот файл (`app/auth/queries/users/get_list.py`) как образец для любого нового «списочного» query-хендлера с пагинацией: `GetListArticlesQuery` / `GetListArticlesQueryHandler` в новом модуле строятся ровно по этой же схеме.

**5. DI-провайдер:**

```python
class ArticleModuleProvider(Provider):
    scope = Scope.REQUEST

    article_repository = provide(ArticleRepository)
    create_handler = provide(CreateArticleCommandHandler)
    get_list_handler = provide(GetListArticlesQueryHandler)

    @decorate
    def register_commands(self, registry: CommandRegisty) -> CommandRegisty:
        registry.register_command(CreateArticleCommand, CreateArticleCommandHandler)
        return registry

    @decorate
    def register_queries(self, registry: QueryRegistry) -> QueryRegistry:
        registry.register_query(GetListArticlesQuery, GetListArticlesQueryHandler)
        return registry
```

**6. Роутер:**

```python
router = APIRouter(prefix="/articles", route_class=DishkaRoute)

@router.post("/", status_code=201)
async def create_article(
    data: ArticleCreateRequest,
    mediator: FromDishka[BaseMediator],
) -> ArticleResponse:
    dto = await mediator.handle_command(CreateArticleCommand(title=data.title, user_id=...))
    return ArticleResponse.model_validate(dto)
```

**7. Регистрация модуля:**

```python
# app/core/di/container.py
from app.new_module.providers import ArticleModuleProvider

def create_container(...) -> AsyncContainer:
    return make_async_container(
        *get_core_providers(),
        AuthModuleProvider(),
        ArticleModuleProvider(),   # ← добавить
    )

# app/main.py
from app.new_module.routers import router_v1 as article_router_v1

def setup_router(app: FastAPI) -> None:
    app.include_router(auth_router_v1, prefix=app_config.API_V1_STR)
    app.include_router(article_router_v1, prefix=app_config.API_V1_STR)  # ← добавить
```

### 3. Соглашения по именованию

| Элемент | Стиль | Пример |
|---------|-------|--------|
| Модуль | существительное (мн. число) | `articles`, `orders` |
| Команда | глагол + существительное | `CreateArticle`, `PublishPost` |
| Событие | прошедшее время | `ArticleCreated`, `OrderShipped` |
| Query | `Get` + существительное | `GetListArticles`, `GetArticleById` |
| Фильтр | существительное + `Filter` | `ArticleFilter` |
| Репозиторий | существительное + `Repository` | `ArticleRepository` |