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
Provides core services using your existing implementations.

```python
@provide
def taskiq_broker(self) -> AsyncBroker:
    return broker  # Your existing Taskiq broker

@provide  
def queue_service(self, taskiq_broker: AsyncBroker) -> QueueServiceInterface:
    return TaskiqQueueService(broker=taskiq_broker)  # Your existing service

@provide
def mail_service(self, queue_service: QueueServiceInterface) -> MailServiceInterface:
    return AioSmtpLibMailService(queue_service=queue_service)  # Your existing service
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

## Key Features

### ✅ **Works with Your Existing Services**
- Uses your original `AioSmtpLibMailService` with `queue_service` dependency
- Uses your original `TaskiqQueueService` with `AsyncBroker` dependency
- Preserves all existing functionality and dependencies

### ✅ **Complete Modularity**
- Each module has its own DI providers
- Easy to add new modules without affecting existing ones
- Clear separation of concerns

### ✅ **Multiple Architectural Patterns**
- **Repository Pattern**: Data access abstraction
- **CQRS (Command Query Responsibility Segregation)**: Separate read/write operations
- **Mediator Pattern**: Decoupled request handling
- **Event-Driven Architecture**: Asynchronous event handling

### ✅ **Comprehensive Service Coverage**
- **Database**: PostgreSQL with SQLAlchemy async sessions
- **Caching**: Redis-based caching with aiocache
- **Email**: Your existing `AioSmtpLibMailService` with SMTP and templating
- **Queuing**: Your existing `TaskiqQueueService` with background task processing
- **Logging**: Structured logging with multiple handlers
- **Configuration**: Type-safe configuration management

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

### 3. Using Your Existing Services

```python
from app.core.services.mail.service import MailServiceInterface
from app.core.services.queue.service import QueueServiceInterface

@app.post("/send-notification")
async def send_notification(
    # This will inject your AioSmtpLibMailService
    mail_service: MailServiceInterface = inject(MailServiceInterface),
    # This will inject your TaskiqQueueService  
    queue_service: QueueServiceInterface = inject(QueueServiceInterface),
):
    # Your services work exactly as before
    await mail_service.send_plain("Subject", "user@example.com", "Body")
    
    # Queue tasks using your existing TaskiqQueueService
    task_id = await queue_service.push(SomeTask, {"data": "value"})
```

### 4. Using the Mediator Pattern

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

## Scopes

The DI system uses different scopes for different types of dependencies:

- **APP Scope**: Singletons shared across the application (configs, services, mediator)
- **REQUEST Scope**: Per-request instances (database sessions, repositories, handlers)

## Benefits of This Approach

### 1. **Preserves Your Existing Code**
- No changes to your `AioSmtpLibMailService` or `TaskiqQueueService`
- All existing functionality maintained
- Existing dependencies respected

### 2. **Modularity**
Each module (auth, core, etc.) has its own DI providers, making the system highly modular and maintainable.

### 3. **Testability**
Easy to mock dependencies for testing by providing test-specific providers.

### 4. **Type Safety**
Full type safety with proper type hints and IDE support.

### 5. **Performance**
Dishka provides excellent performance with minimal overhead.

### 6. **Flexibility**
Supports multiple patterns:
- Direct injection
- Mediator pattern (CQRS)
- Event-driven architecture
- Repository pattern

## Service Dependencies

Your existing services are properly wired:

```python
# TaskiqQueueService gets the broker from your existing init.py
TaskiqQueueService(broker=broker)

# AioSmtpLibMailService gets the queue service it needs
AioSmtpLibMailService(queue_service=queue_service)
```

This preserves all functionality while adding comprehensive DI capabilities.

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

This DI system provides a robust, scalable foundation while preserving all your existing service implementations and their dependencies.