# FastAPI Template

## Содержание

1. [Введение](#введение)
2. [Архитектура](#project-structure)
    - [База данных](#database-layer)
    - [API слой](#api-layer)
    - [Конфигурация](#config)
    - [Dependency Injection](#dependency-injection)
3. [Безопасность](#security)
    - [Политики доступа](#policies)
4. [Core Services](#core-services)
    - [Events System](#events)
    - [Cache Service](#cache-service)
    - [Queue Service](#queue-service)
    - [Mail Service](#mail-service)
    - [Logging Service](#logging-service)

## Введение


Вдохновлен [Starter Kit](https://github.com/arctikant/fastapi-modular-monolith-starter-kit)


### Project Structure

```
fastapi_template/
├── alembic/              # Database migrations
├── app/                  # Application package
│   ├── main.py         # Application entry point
│   ├── pre_start.py    # Pre-start checks and initialization
│   ├── init_data.py    # Initial data setup
│   ├── consumers.py    # FastStream consumers
│   ├── core/            # Core functionality
│   │   ├── api/         # API related tools
│   │   ├── configs/     # Configuration management
│   │   ├── db/         # Database utilities
│   │   ├── di/         # Dependency injection setup
│   │   ├── events/     # Event system
│   │   ├── log/        # Logging configuration
│   │   └── services/   # Core services
│   └── auth/           # Auth module (example module structure)
│       ├── commands/   # Command handlers
│       ├── di/         # Module DI setup
│       ├── events/     # Module specific events
│       ├── models/     # Database models
│       ├── queries/    # Query handlers
│       ├── routes/     # API routes
│       └── services/   # Module services
├── migrations/          # Alembic migrations
└── tests/              # Test suite
```

### Database Layer

**Used:**

- Database: [PostgreSQL](https://www.postgresql.org)
- PostgreSQL adapter: [asyncpg](https://pypi.org/project/asyncpg/)
- ORM: [SQLAlchemy](https://www.sqlalchemy.org) 2.0+ (async)
- Migration tool: [Alembic](https://github.com/sqlalchemy/alembic)

**Key Notes:**

- `app.core.db.BaseModel` — реализует общую логику модели. Все пользовательские модели должны её наследовать. Сам `BaseModel` наследует от `sqlalchemy.orm.DeclarativeBase`.
- `app.core.db.SoftDeleteMixin` - Реализует функцию «мягкого» удаления. Чтобы добавить логику «мягкого» удаления для вашей конкретной модели, вам просто нужно унаследовать `SoftDeleteMixin`.
- Все модели должны быть импортированы в `app/core/models.py`, чтобы Alembic мог их видеть и работать с ними.

### API Layer

**Used:**

- Rate limiting tool: [fastapi-limiter](https://github.com/long2ice/fastapi-limiter)
- Storage provider: [Redis](https://redis.io)

**Key Notes:**

- Для группировки связанных маршрутов следует использовать `APIRouter` из `fastapi`. Их следует разместить в отдельных файлах, расположенных в `routes.v<api-version>` ваших модулей. Например: `app.auth.routes.v1.users.py`.

- Каждый модуль имеет маршрутизатор верхнего уровня, который объединяет все групповые маршрутизаторы в один главный. Например: `app.auth.routers.py`.

- Маршрутизатор верхнего уровня из каждого модуля должен быть зарегистрирован в маршрутизаторе приложения в `app.main.py`

- `app.core.api.builder.ListParamsBuilder` — зависимость, которая анализирует и формирует список параметров запроса. Она использует модели Pydantic `app.core.api.schemas.ListParams`, `app.core.api.schemas.SortParam`, `app.core.api.schemas.FilterParam`. Поэтому мы можем расширить их и настроить правила валидации. Например, в `app.auth.schemas.user.py`:

    ```python
    from app.core.api.schemas import FilterParam, ListParams, SortParam

    class UserSortParam(SortParam):
        field: Literal['id', 'username', 'status_id', 'created_at']

    class UserFilterParam(FilterParam):
        field: Literal['id', 'username', 'status_id']

    class UserListParams(ListParams):
        sort: list[UserSortParam] | None = Field(None, description='Sorting parameters')
        filters: list[UserFilterParam] | None = Field(None, description='Filtering parameters')
    ```

    Затем мы создаем экземпляр `app.core.api.builder.ListParamsBuilder` и используем его в функции операции пути:    

    ```python
    from app.auth.schemas.user import UserFilterParam, UserListParams, UserResponse, UserSortParam
    from app.core.api.builder import ListParamsBuilder, PaginatedResponse
    
    list_params_builder = ListParamsBuilder(UserListParams, UserSortParam, UserFilterParam)
    
    @router.get('')
    async def get_list(request: UserListParams = Depends(list_params_builder)
    ) -> PaginatedResponse[list[UserResponse]]:
        ...
    ```
    
- `app.core.api.rate_limiter.ConfigurableRateLimiter` - это просто простая оболочка для зависимости `RateLimiter` из пакета `fastapi_limiter`, которая добавляет возможность включать/отключать ограничение из конфигурации.

    Вот как можно использовать ограничитель `APIRouter`:

    ```python
    from app.core.api.rate_limiter import ConfigurableRateLimiter

    router = APIRouter(dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60))])
    ```

    Практически то же самое для функции операции пропуска:

    ```python
    from app.core.api.rate_limiter import ConfigurableRateLimiter

    @app.get("/", dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60))])
    async def index():
        ...
    ```


### Config

**Key Notes:**
- Конфигурации приложения можно получить через `app.core.configs.app_config`.
- Каждый модуль должен иметь свой собственный `config.py` (при необходимости), который должен быть унаследован от `app.core.configs.BaseConfig`.
- Все конфигурации извлекают параметры из файла `.env`.
- `.env.example` — это всего лишь пример, описывающий все используемые параметры. Его следует скопировать в `.env` при первом развёртывании приложения.

### Dependency Injection.

В проекте используется сложная система DI, основанная на фреймворке Diska:

**Container Setup**
- Модульная регистрация зависимостей в папках `di/`
- Поддержка как синхронных, так и асинхронных зависимостей

**Key Features**
- **Scoped Lifetime Management**: Поддержка времен жизни `singleton`, `scoped` и `session`
- **Integration with FastAPI and FastStream**:
```python
# FastStream integration example
@asynccontextmanager
async def lifespan(context: ContextRepo):
    logger.info("Lifespan")
    yield

def init_consumers() -> FastStream:
    container = create_container(FastStreamProvider())
    setup_dishka(container=container, app=app, auto_inject=True)
```

**Module folder di**

```
├── __init__.py
├── commands.py
├── events.py
├── handlers.py
├── queries.py
├── repositories.py
└── services.
```

### Policies

**Key Notes:**

- Все файлы политик должны быть размещены в каталоге `policies` в нашем модуле.

Очень полезно разделить логику доступа к действиям и саму логику действий. Для реализации этого не требуется устанавливать никакие сторонние библиотеки. В шаблоне сейчас нет места для этой логики, поэтому я просто покажу вам пример.

В вашем `app.our_module.policies.users.py`:

```python
from app.auth.deps import ActiveUser
from app.auth.exceptions import ActionNotAllowed

async def can_update(user: ActiveUser) bool:
    # Any logic we need to restrict access to this action.
    if not user.is_admin:
        raise ActionNotAllowed("You don't have permission to update the user")
    
    return True
```

Затем мы можем использовать его в нашей функции операции пути:

```python
@router.patch('/{user_id}', dependencies=[Depends(can_update)])
async def update(user_id: int) -> None:
    ...
```

Как видите, система DI позволяет нам легко и довольно элегантно добавлять эти проверки в наши маршруты. Мы также можем использовать её где угодно в нашем коде, например, в ваших сервисах. Достаточно просто передать необходимые параметры в нашу функцию:

```python
from app.auth.exceptions import ActionNotAllowed

async def update_status(user_id: int, status_id: UserStatus) -> User:
    user = await self.get(user_id)

    if not await can_update(user):
        raise ActionNotAllowed("You don't have permission to update the user.")
```

Такой подход позволяет нам хранить логику доступа к действиям в одном месте и использовать её повторно при необходимости.

## Services

### Events

**Used:**

- `EventBus`: Индивидуальная реализация на основе шаблона Mediator
- `DI Container`: [Dishka](https://github.com/reagento/dishka)


**Key Notes**

1. **Event System Components:**
     - `BaseEvent` - Базовый класс для всех событий (из `app.core.events.event`)
     - `EventRegisty` - Реестр обработчиков событий
     - `BaseEventBus` - Интерфейс для обработки событий
     - `MediatorEventBus` - Основная реализация EventBus

2. **Creating New Events:**
   ```python
    from dataclasses import dataclass
    from app.core.events.event import BaseEvent

    @dataclass(frozen=True)
    class UserCreatedEvent(BaseEvent):
        email: str
        username: str
        __event_name__: str = "user_created"  # Unique event identifier
    ```

3. **Creating Event Handlers:**
    ```python
    @dataclass(frozen=True)
    class SendVerifyEventHandler(BaseEventHandler[CreatedUserEvent, None]):
        user_service: UserService

        async def __call__(self, event: CreatedUserEvent) -> None:
            await self.user_service.send_verify(email=event.email)
   ```

4. **Dispatching Events:**
    ```python
    # In your models
    class User(BaseModel):
        @classmethod
        def create(cls, email: str, username: str, password_hash: str) -> "User":
            user = User(
                email=email,
                username=username,
                password_hash=password_hash
            )

            user.register_event(
                CreatedUserEvent(
                    email=email,
                    username=username
                )
            )
            return user
    ```

**Best Practices:**

1. **Event Naming:**
     - Названия событий должны быть описательными и однозначными.
     - Определите `__event_name__` для каждого события

2. **Handler Organization:**
     - Храните обработчики в отдельном каталоге `events` внутри вашего модуля.
     - Один обработчик на файл для лучшей организации.
     - Следуйте шаблону: `<module>/events/<entity>/<event_name>.py`

3. **Event Data:**
     - События должны быть неизменяемыми (используйте `@dataclass(frozen=True)`)
     - Включайте в события только необходимые данные
     - По возможности используйте идентификаторы вместо полных объектов


### Cache service

**Used:**

- Async caching tool: [aiocache](https://github.com/aio-libs/aiocache)
- Storage provider: [Redis](https://redis.io)

**Key Notes:**

- `@cached` decorator from `app.core.deps` should be used to add caching for path operation function.
- `CacheService` dependency from `app.core.deps` should be used to retrieve an instance that implements `app.core.services.cache.CacheServiceInterface` from FastAPI DI system.

This is just typical cache service that provides a convenient way to cache path operation functions:

```python
from app.core.deps import cached

@app.get("/items/{item_id}")
@cached(ttl=60, key_builder=lambda f, *args, **kwargs: f"item:{kwargs['item_id']}")
async def get(item_id: int):
    ...
```

As well as any arbitrary data:

```python
from app.core.deps import CacheService

@router.get('/')
async def index(cache_service: CacheService) -> Response:
    ...
    cache_service.set(key='key', value='value', ttl=60)
    ...
    cache_service.get('key')
    ...
    cache_service.delete('key')
```

### Queue service

**Used:**

- Async distributed task manager: [Taskiq](https://taskiq-python.github.io)
- Taskiq Redis broker: [Taskiq-Redis](https://github.com/taskiq-python/taskiq-redis)
- Message broker: [Redis](https://redis.io)

**Key Notes:**
- Каждая задача очереди должна быть унаследована от `app.core.services.queue.task.BaseTask`, иметь атрибут `__task_name__` и реализовывать метод `run(...)`.
- Все задачи модуля должны быть зарегистрированы в `core/di/tasks.py`.

Вот как могут выглядеть задачи очереди:

```python
from app.core.services.queue import BaseTask

class SendEmail(BaseTask):
    __task_name__ = 'mail.send'

    @staticmethod
    @inject
    async def run(content: str, email_data: dict, smtp_config: FromDishka[SMTPConfig]) -> None:
        ...
        message = EmailMessage()  
        ...
        await aiosmtplib.send(message, **smtp_config)
```

Чтобы отправить его в очередь, нам следует использовать `QueueService`:

```python
from app.core.deps import QueueService

@router.get('/')
async def index(queue_service: FromDishka[QueueService]) -> Response:
    ...
    await queue_service.push(
        task=SendEmail,  
        data={'content': template.render(), 'email_data': email_data},
    )
```

### Mail service

**Used:**

- Async email handling: [aiosmtplib](https://aiosmtplib.readthedocs.io/en/stable)
- Template engine: [Jinja2](https://jinja.palletsprojects.com)

**Key Notes:**

- Каждый шаблон электронной почты должен наследовать `app.core.services.mail.template.BaseTemplate` и реализовывать методы `_get_dir(...)` и `_get_name(...)`.
- Все классы шаблонов электронной почты должны быть помещены в `emails.templates.py` каждого модуля. Сами HTML-шаблоны должны быть помещены в каталог `emails.views`.
- Отправка почты может выполняться в фоновом режиме с помощью `QueueService`.

Пример класса шаблона электронной почты:

```python
from app.core.services.mail import BaseTemplate

class UserRegistration(BaseTemplate):
    def __init__(self, username: str, project_name: str):
        self.username = username
        self.project_name = project_name
        
    def _get_dir(self) -> Path:
        return Path('app/auth/emails/views')

    def _get_name(self) -> str:
        return 'user_registration.html'
```

И HTML-шаблон `user_registration.html`:

```python
<h1> Hello {{ username }}!</h1>

<p>You have successfully registered on <b>{{ project_name }}</b>.</p>
<p>Thank you and welcome to your new account!</p>
```

Для отправки электронного письма нам следует использовать `MailService`:

```python

@router.get('/')
async def index(mail_service: FromDishka[MailService]) -> Response:
    ...
    email_data = EmailData(subject='Successful registration', recipient=user.email)
    template = UserRegistration(username=user.username, project_name=app_config.PROJECT_NAME)
    mail_service.send(template=template, email_data=email_data)

    # Or to send on background using QueueService
    mail_service.queue(template=template, email_data=email_data)
```


### Logging service

**Used:**
- Logging solution: [structlog](https://www.structlog.org/en/stable)

**Key Notes:**
- Мы можем настроить конфигурацию structlog в `app/core/log/init.py`.
- Так же добавлен в `app/core/log/processors.py` обработка логов.

`logger` можно использовать следующим образом:

```python
import logging

logger = logging.getLogger(__name__)

await logger.info('Something happened')
```

### Message Processing

**Used:**
- Message Processing: [FastStream](https://faststream.airtry.dev/)
- Message Broker: [Redis](https://redis.io)

**Key Notes:**

1. **Consumer Setup:**
   ```python
   from faststream.redis import RedisBroker
   from faststream import FastStream
   from dishka import Provider, Scope, provide

   broker = RedisBroker("redis://localhost:6379")
   app = FastStream(broker)

   @broker.subscriber(SomeEvent.getname())
   async def handle_message(message: dict):
       print(message)
   ```

2. **Integration with DI:**
   ```python
   class FastStreamProvider(Provider):
       scope = Scope.APP

       @provide
       def get_broker(self) -> RedisBroker:
           return broker
   ```

3. **Lifecycle Management:**
   ```python
   @asynccontextmanager
   async def lifespan(context: ContextRepo):
       logger.info("Starting FastStream")
       yield
       logger.info("Shutting down FastStream")

   def init_consumers() -> FastStream:
       container = create_container(FastStreamProvider())
       setup_dishka(container=container, app=app, auto_inject=True)
       return app
   ```

### Middleware

**Used:**
- FastAPI middleware system
- Custom middleware implementations

**Key Notes:**

1. **Core Middlewares:**
    - `ContextMiddleware` - Добавляет уникальный ID к каждому запросу
    - `LoggingMiddleware` - Логирует информацию о запросах и ответах

2. **Пример Custom Middleware:**
    ```python
    class ContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request.state.request_id = uuid4()
        with structlog.contextvars.bound_contextvars(request_id=str(request.state.request_id)):
            return await call_next(request)
    ```

3. **Регистрация Middleware:**
   ```python
    from app.core.middlewares import ContextMiddleware, LoggingMiddleware

    app = FastAPI()
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ContextMiddleware)

   ```

4. **Middleware Order:**
    - ContextMiddleware → LoggingMiddleware  → Application
    - Порядок важен: например, request_id должен быть первым, чтобы ID был доступен для логирования


## Application Lifecycle

### Startup Sequence

1. **Pre-start проверки** (`pre_start.py`):
   ```python
    @retry(
        stop=stop_after_attempt(max_tries),
        wait=wait_fixed(wait_seconds),
        before=before_log(logger, logging.INFO),  # type: ignore
        after=after_log(logger, logging.INFO),  # type: ignore
    )
    async def init(db: AsyncSession) -> None:
        try:
            await db.execute(select(1))
        except Exception as exc:
            logger.exception('database_init_error')
            raise exc
   ```

2. **Инициализация приложения** (`main.py`):
    ```python
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        redis_client = redis.from_url(app_config.redis_url)
        await FastAPILimiter.init(redis_client)
        message_broker = await app.state.dishka_container.get(BaseMessageBroker)
        await message_broker.start()
        yield
        await redis_client.aclose()
        await message_broker.close()
        await app.state.dishka_container.close()
    
    def init_app() -> FastAPI:

        app = FastAPI(
            openapi_url=f'{app_config.API_V1_STR}/openapi.json' if app_config.ENVIRONMENT in ['local', 'staging'] else None,
            lifespan=lifespan,
        )

        configure_logging()
        container = create_container()
        setup_dishka(container=container, app=app)

        setup_middleware(app, container)
        setup_router(app)

        app.add_exception_handler(ApplicationException, handle_application_exeption) # type: ignore

        return app


   ```

3. **Инициализация данных** (`init_data.py`):
    ```python
    async def create_first_data(db: AsyncSession) -> None:
        if not await db.get(User, 1):
            user = User.create(
                email="admin@example.com",
                username="admin",
                password_hash=hash_password("admin")
            )
            db.add(user)
            await db.commit()

    async def init_data() -> None:
        """Создание начальных данных при первом запуске."""
        async for db in get_session():
            await create_first_data(db)
            break
    ```


## Создание нового модуля

### 1. Структура модуля

```
new_module/
├── __init__.py
├── models/              # Модели данных
│   ├── __init__.py
│   └── entity.py
├── repositories/        # Репозитории
│   ├── __init__.py
│   └── entity.py
├── services/           # Бизнес-логика
│   ├── __init__.py
│   └── entity.py
├── routes/                # API endpoints
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── entity.py
├── schemas/            # Pydantic models
│   ├── __init__.py
│   └── entity.py
├── commands/           # Command handlers
│   ├── __init__.py
│   └── entity/
│       ├── __init__.py
│       └── create.py
├── queries/           # Query handlers
│   ├── __init__.py
│   └── entity/
│       ├── __init__.py
│       └── get.py
├── events/            # Event handlers
│   ├── __init__.py
│   └── entity/
│       ├── __init__.py
│       └── created.py
├── di/                # DI configuration
│   ├── __init__.py
│   ├── repositories.py
│   ├── services.py
│   ├── commands.py
│   ├── queries.py
│   └── events.py
|
└── routers.py # Main router module
```

### 2. Шаги создания нового модуля

1. **Создание моделей данных:**
    ```python
    from app.core.db import BaseModel, DateMixin

    class Entity(BaseModel, DateMixin):
        __tablename__ = "entities"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))
    ```

2. **Создание репозитория:**
    ```python

    class EntityRepository:
        session: AsyncSession

        async def create(self, entity: Entity) -> None:
            self.add(entity)
    ```

3. **Создание сервиса:**
    ```python
    @dataclass
    class EntityService:
        repository: EntityRepository

        async def create(self, data: EntityCreate) -> Entity:
            entity = Entity(**data.model_dump())
            await self.repository.create(entity)
            return entity
    ```

4. **Настройка DI:**
    ```python
    # di/repositories.py
    class ModuleRepositoryProvider(Provider):
        scope = Scope.REQUEST
        entity_repository = provide(EntityRepository)

    # di/services.py
    class ModuleServiceProvider(Provider):
        scope = Scope.REQUEST
        entity_service = provide(EntityService)
    ```

5. **Создание API endpoints:**
    ```python
    router = APIRouter(prefix="/api/v1/entities")

    @router.post("/")
    async def create_entity(
        data: EntityCreate,
        service: FromDishka[EntityService],
    ) -> EntityResponse:
        entity = await service.create(data)
        return EntityResponse.model_validate(entity)
    ```

6. **Регистрация модуля:**
    ```python
    # В core/di/container.py
    def create_container(*app_providers) -> AsyncContainer:
        providers = [
            *get_core_providers(),
            *get_new_module_providers(),  # Добавляем providers нового модуля
        ]
        return make_async_container(*providers, *app_providers)

    # В main.py или routers.py
    app.include_router(new_module_router, prefix="/api/v1")

    #В core/di/mediator.py
    class MediatorProvider(Provider):
        scope = Scope.APP

        @provide
        def command_registry(self) -> CommandRegisty:
            registry = CommandRegisty()
            register_MODULE_command_handlers(registry)
            return registry

        @provide
        def query_registry(self) -> QueryRegisty:
            registry = QueryRegisty()
            register_MODULE_query_handlers(registry)
            return registry
    
    #В core/di/events.py
    class EventProvider(Provider):
        scope = Scope.APP

        @provide
        def event_handler_registry(self) -> EventRegisty:
            registry = EventRegisty()
            register_MODULE_event_handlers(registry)
            return registry
    ```

### 3. Лучшие практики

1. **Организация кода:**
    - Следуйте принципу единой ответственности
    - Разделяйте слои абстракции
    - Используйте типизацию

2. **Именование:**
    - Модули: существительные во множественном числе (users, orders)
    - Команды: глаголы (create_user, update_order)
    - События: прошедшее время (user_created, order_updated)

3. **Тестирование:**
    - Создавайте тесты одновременно с кодом
    - Следуйте структуре модуля в тестах
    - Используйте фабрики для создания тестовых данных
