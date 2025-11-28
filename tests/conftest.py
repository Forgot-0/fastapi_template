import asyncio
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass, field
from typing import Any, Iterable

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import AsyncRedisContainer

from app.core.db.base_model import BaseModel
from app.core.di.container import create_container
from app.core.events.event import BaseEvent, EventRegisty
from app.core.events.service import BaseEventBus
from app.core.services.mail.service import BaseMailService, EmailData
from app.core.services.mail.template import BaseTemplate
from app.init_data import create_first_data
from app.main import init_app


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16.3-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container() -> Generator[AsyncRedisContainer, None, None]:
    with AsyncRedisContainer("redis:7.2-alpine") as redis:
        yield redis


@pytest_asyncio.fixture(scope="session")
async def db_engine(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncEngine, None]:
    database_url = postgres_container.get_connection_url(driver="asyncpg")

    engine = create_async_engine(
        database_url,
        poolclass=NullPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def load_initial_data(db_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    session_maker = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        await create_first_data(session)

    yield


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:

    connection = await db_engine.connect()
    transaction = await connection.begin()

    session_maker = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    session = session_maker()
    await connection.begin_nested()

    @event.listens_for(session.sync_session, "after_transaction_end")
    def restart_savepoint(session: Any, transaction: Any) -> None:
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()

@pytest_asyncio.fixture
async def redis_client(redis_container: AsyncRedisContainer) -> AsyncGenerator[Redis, None]:
    client = await redis_container.get_async_client()

    yield client

    await client.flushall()
    await client.aclose()


@dataclass
class MockMailService(BaseMailService):
    sent_emails: list

    async def send(self, template: BaseTemplate, email_data: EmailData) -> None:
        self.sent_emails.append({"template": template, "data": email_data})

    async def queue(self, template: BaseTemplate, email_data: EmailData) -> str:
        self.sent_emails.append({"template": template, "data": email_data})
        return "task_id"

    async def send_plain(self, subject: str, recipient: str, body: str) -> None:
        ...

    async def queue_plain(self, subject: str, recipient: str, body: str) -> str:
        return "task_id"


@pytest.fixture
def mock_mail_service() -> MockMailService:
    return MockMailService([])


@dataclass
class MockEventBus(BaseEventBus):
    published_events: list[BaseEvent] = field(default_factory=list)

    async def publish(self, events: Iterable[BaseEvent]) -> None:
        self.published_events.extend(events)


@pytest.fixture
def mock_event_bus() -> BaseEventBus:
    return MockEventBus(event_registy=EventRegisty())

@pytest_asyncio.fixture
async def di_container(
    db_session: AsyncSession,
    redis_client: Redis,
    mock_event_bus: BaseEventBus
) -> AsyncGenerator[AsyncContainer, None]:

    class TestProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def get_session(self) -> AsyncGenerator[AsyncSession]:
            yield db_session

        @provide(scope=Scope.APP)
        async def get_redis(self) -> Redis:
            return redis_client

        @provide(scope=Scope.APP)
        async def get_mock_event_bus(self) -> BaseEventBus:
            return mock_event_bus

    container = create_container(TestProvider())

    yield container

    await container.close()


@pytest.fixture
async def app(di_container: AsyncContainer) -> FastAPI:
    app = init_app()
    app.state.dishka_container = di_container
    return app


@pytest.fixture
async def client(app: FastAPI, redis_client: Redis) -> AsyncGenerator[AsyncClient, None]:
    await FastAPILimiter.init(redis_client)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac



@pytest.fixture
def mock_now() -> float:
    return 1704067200.0  # 2024-01-01 00:00:00 UTC


@pytest.fixture
def app_config_override() -> dict[str, Any]:
    return {
        "ENVIRONMENT": "testing",
        "RATE_LIMITER_ENABLED": False,
        "SQL_ECHO": False,
    }


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: Unit тесты")
    config.addinivalue_line("markers", "integration: Integration тесты")
    config.addinivalue_line("markers", "slow: Медленные тесты")
    config.addinivalue_line("markers", "auth: Тесты модуля аутентификации")

