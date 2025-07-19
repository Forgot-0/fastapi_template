# Dependency Injection with Dishka

This document explains the comprehensive Dependency Injection (DI) system implemented using [Dishka](https://github.com/aiogram/dishka) for our modular FastAPI application.

## Architecture Overview

The DI system is organized into several layers:

```
app/
├── core/di/               # Core DI infrastructure
│   ├── __init__.py       # Main exports
│   ├── container.py      # Main container setup
│   ├── fastapi.py        # FastAPI integration
│   ├── config.py         # Configuration provider
│   ├── db.py             # Database provider
│   ├── cache.py          # Cache provider
│   ├── services.py       # Core services provider
│   ├── mediator.py       # CQRS mediator provider
│   └── events.py         # Event system provider
└── auth/di/              # Auth module DI providers
    ├── __init__.py       # Auth providers export
    ├── repositories.py   # Auth repositories
    ├── commands.py       # Auth command handlers
    ├── queries.py        # Auth query handlers
    └── events.py         # Auth event handlers
```

## Core Providers

### 1. ConfigProvider (`config.py`)
Provides application configuration as a singleton.

```python
@provide
def get_app_config(self) -> AppConfig:
    return app_config
```

### 2. DBProvider (`db.py`)
Manages database connections and sessions.

```python
@provide
async def get_engine(self) -> AsyncIterable[AsyncEngine]: ...

@provide(scope=Scope.REQUEST)
async def get_session(self, marker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]: ...
```

### 3. CacheProvider (`cache.py`)
Provides Redis-based caching.

```python
@provide
async def cache_service(self, cache_provider: BaseCache) -> CacheServiceInterface: ...
```

### 4. ServiceProvider (`services.py`)
Provides core services like mail, queue, and logging.

```python
@provide
def mail_service(self, config: AppConfig) -> MailServiceInterface: ...

@provide
def queue_service(self, config: AppConfig) -> QueueServiceInterface: ...

@provide
def log_service(self, config: AppConfig) -> LogService: ...
```

### 5. MediatorProvider (`mediator.py`)
Provides CQRS mediator pattern implementation.

```python
@provide
def mediator(self, container: Container, command_registry: CommandHandlerRegistry, query_registry: QueryHandlerRegistry) -> BaseMediator: ...
```

### 6. EventProvider (`events.py`)
Provides event bus for event-driven architecture.

```python
@provide
def event_bus(self, event_registry: EventHandlerRegistry) -> BaseEventBus: ...
```

## Module Providers (Auth Example)

### AuthRepositoryProvider (`auth/di/repositories.py`)
Provides auth-specific repositories.

```python
@provide
def user_repository(self) -> UserRepository: ...

@provide
def token_repository(self) -> TokenRepository: ...
```

### AuthCommandProvider (`auth/di/commands.py`)
Provides command handlers for auth operations.

```python
@provide
def register_command_handler(self, session: AsyncSession, event_bus: BaseEventBus, user_repository: UserRepository) -> RegisterCommandHandler: ...
```

### AuthQueryProvider (`auth/di/queries.py`)
Provides query handlers for auth operations.

```python
@provide
def get_user_by_id_query_handler(self, session: AsyncSession, user_repository: UserRepository) -> GetUserByIdQueryHandler: ...
```

### AuthEventProvider (`auth/di/events.py`)
Provides event handlers for auth events.

```python
@provide
def created_user_event_handler(self, mail_service: MailServiceInterface, queue_service: QueueServiceInterface) -> CreatedUserEventHandler: ...
```

## Usage Examples

### 1. Basic FastAPI Integration

```python
from fastapi import FastAPI
from app.core.di import setup_di

app = FastAPI()
setup_di(app)  # This sets up Dishka integration
```

### 2. Direct Dependency Injection

```python
from app.core.di import inject
from app.auth.repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = inject(AsyncSession),
    user_repo: UserRepository = inject(UserRepository),
):
    user = await user_repo.get_by_id(session, user_id)
    return {"user": user.to_dict() if user else None}
```

### 3. Using the Mediator Pattern

```python
from app.core.di import inject
from app.core.mediators.base import BaseMediator
from app.auth.queries.users.get_by_id import GetUserByIdQuery

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    mediator: BaseMediator = inject(BaseMediator),
):
    query = GetUserByIdQuery(user_id=user_id)
    result = await mediator.handle_query(query)
    return {"user": result}
```

### 4. Service Injection

```python
from app.core.services.mail.service import MailServiceInterface
from app.core.services.cache.base import CacheServiceInterface

@app.post("/send-notification")
async def send_notification(
    mail_service: MailServiceInterface = inject(MailServiceInterface),
    cache_service: CacheServiceInterface = inject(CacheServiceInterface),
):
    # Use services...
```

## Scopes

The DI system uses different scopes for different types of dependencies:

- **APP Scope**: Singletons shared across the application (configs, services, mediator)
- **REQUEST Scope**: Per-request instances (database sessions, repositories, handlers)

## Benefits of This Approach

### 1. **Modularity**
Each module (auth, core, etc.) has its own DI providers, making the system highly modular and maintainable.

### 2. **Testability**
Easy to mock dependencies for testing by providing test-specific providers.

### 3. **Type Safety**
Full type safety with proper type hints and IDE support.

### 4. **Performance**
Dishka provides excellent performance with minimal overhead.

### 5. **Flexibility**
Supports multiple patterns:
- Direct injection
- Mediator pattern (CQRS)
- Event-driven architecture
- Repository pattern

## Adding New Dependencies

### 1. Create a Provider

```python
from dishka import Provider, Scope, provide

class NewModuleProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def new_service(self, dependency: SomeDependency) -> NewService:
        return NewService(dependency)
```

### 2. Register the Provider

```python
# In app/new_module/di/__init__.py
def get_new_module_providers():
    return [NewModuleProvider()]

# In app/core/di/container.py
from app.new_module.di import get_new_module_providers

def create_container() -> Container:
    providers = [
        # ... existing providers
        *get_new_module_providers(),
    ]
    return make_container(*providers)
```

### 3. Use the Dependency

```python
from app.core.di import inject

@app.get("/endpoint")
async def endpoint(new_service: NewService = inject(NewService)):
    return await new_service.do_something()
```

## Best Practices

1. **Keep providers focused**: Each provider should handle a specific domain
2. **Use interfaces**: Depend on abstractions, not concrete implementations
3. **Proper scoping**: Use REQUEST scope for per-request dependencies, APP scope for singletons
4. **Type hints**: Always provide proper type hints for better IDE support
5. **Documentation**: Document complex provider setups

## Testing with DI

```python
import pytest
from dishka import make_container
from app.core.di import get_core_providers

@pytest.fixture
def test_container():
    # Create container with test-specific providers
    providers = get_core_providers()
    # Add test providers or override existing ones
    return make_container(*providers)

def test_service(test_container):
    with test_container() as request_scope:
        service = request_scope.get(SomeService)
        result = service.do_something()
        assert result == expected_result
```

This DI system provides a robust, scalable, and maintainable foundation for the application while supporting multiple architectural patterns and ensuring type safety throughout the codebase.