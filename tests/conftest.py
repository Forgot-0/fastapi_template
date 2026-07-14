import asyncio
import os
from collections.abc import AsyncGenerator, Callable, Generator
from datetime import timedelta
from typing import Any
from uuid import uuid4

from fastapi.exceptions import RequestValidationError
import pytest
from dishka import AsyncContainer, Provider, Scope, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import AsyncRedisContainer

from app.core.configs.app import app_config
from app.core.db.base_model import BaseModel
from app.core.di.container import create_container
from app.core.events.event import EventRegistry
from app.core.events.service import BaseEventBus
from app.core.exceptions import ApplicationError
from app.core.log.init import configure_logging
from app.core.services.auth.dto import JwtTokenType, UserJWTData
from app.core.services.auth.jwt_manager import JWTManager
from app.core.services.auth.rbac import RBACManagerInterface
from app.core.services.mail.service import BaseMailService
from app.core.services.queues.service import QueueService
from app.core.services.storage.service import StorageService
from app.core.utils import now_utc
from app.init_data import init_data
from app.main import (
    custom_openapi,
    handle_application_exception,
    handle_unknown_exception,
    handle_validation_exception,
    lifespan,
    setup_middleware,
    setup_router
)
from tests.mocks import FakeQueueService, FakeStorageService, MockEventBus, MockMailService


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:18.3") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container() -> Generator[AsyncRedisContainer]:
    with AsyncRedisContainer("redis:7.2-alpine") as redis:
        yield redis


@pytest.fixture(scope="session")
async def db_engine(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncEngine]:
    database_url = postgres_container.get_connection_url(driver="asyncpg")

    engine = create_async_engine(
        database_url,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def load_initial_data(db_engine: AsyncEngine) -> AsyncGenerator[None]:
    session_maker = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        await init_data(session)

    yield


@pytest.fixture
async def db_connection(db_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection]:
    connection = await db_engine.connect()
    transaction = await connection.begin()

    try:
        yield connection
    finally:
        await transaction.rollback()
        await connection.close()


@pytest.fixture
async def db_session(request_container):
    yield await request_container.get(AsyncSession)


@pytest.fixture
async def redis_client(redis_container: AsyncRedisContainer) -> AsyncGenerator[Redis]:
    client = await redis_container.get_async_client()

    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()

@pytest.fixture
def make_user_jwt() -> Callable[..., UserJWTData]:
    def _make_user_jwt(
        *,
        id: str = "1",
        username: str = "user",
        role: str = "user",
        permissions: list[str] | None = None,
        security_level: int = 1,
        device_id: str = "device_1",
    ) -> UserJWTData:
        return UserJWTData(
            id=id,
            username=username,
            roles=[role],
            permissions=permissions or [],
            security_level=security_level,
            device_id=device_id,
        )

    return _make_user_jwt


@pytest.fixture
def user_jwt(make_user_jwt) -> UserJWTData:
    return make_user_jwt()


@pytest.fixture
def super_admin_user_jwt(make_user_jwt) -> UserJWTData:
    return make_user_jwt(role="super_admin", security_level=9)


@pytest.fixture
def create_access_token(jwt_manager: JWTManager):
    def _create(user_jwt: UserJWTData) -> str:
        data = user_jwt.to_dict()
        data["type"] = JwtTokenType.ACCESS
        data["jti"] = str(uuid4())
        data["exp"] = (now_utc() + timedelta(minutes=5)).timestamp()
        data["iat"] = now_utc().timestamp()
        return jwt_manager.encode(data)

    return _create


@pytest.fixture
def create_auth_headers(create_access_token):
    def _headers(user_jwt: UserJWTData) -> dict[str, str]:
        token = create_access_token(user_jwt)
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture
async def di_container(
    db_connection: AsyncConnection,
    redis_client: Redis,
) -> AsyncGenerator[AsyncContainer]:

    class TestProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def get_session(self) -> AsyncGenerator[AsyncSession]:
            session_maker = async_sessionmaker(
                bind=db_connection,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
            session = session_maker()

            try:
                yield session
            finally:
                await session.close()

        @provide(scope=Scope.APP)
        def get_redis(self) -> Redis:
            return redis_client

        @provide(scope=Scope.APP)
        def mail_service(self) -> BaseMailService:
            return MockMailService()

        @provide(scope=Scope.APP)
        def get_mock_event_bus(self, event_registy: EventRegistry) -> BaseEventBus:
            return MockEventBus(event_registy=event_registy)

        @provide(scope=Scope.APP)
        def get_queue_service(self) -> QueueService:
            return FakeQueueService()

        @provide(scope=Scope.APP)
        def get_storage_service(self) -> StorageService:
            return FakeStorageService()

    container = create_container(TestProvider())
    try:
        yield container
    finally:
        await container.close()


@pytest.fixture
async def request_container(di_container: AsyncContainer) -> AsyncGenerator[AsyncContainer]:
    async with di_container() as request:
        yield request

@pytest.fixture
async def mock_mail_service(di_container: AsyncContainer) -> BaseMailService:
    return await di_container.get(BaseMailService)

@pytest.fixture
async def mock_event_bus(di_container: AsyncContainer) -> BaseEventBus:
    return await di_container.get(BaseEventBus)


@pytest.fixture
async def mock_queue_service(di_container: AsyncContainer) -> QueueService:
    return await di_container.get(QueueService)


@pytest.fixture
async def mock_storage_service(di_container: AsyncContainer) -> StorageService:
    return await di_container.get(StorageService)


@pytest.fixture
async def jwt_manager(di_container: AsyncContainer) -> JWTManager:
    return await di_container.get(JWTManager)


@pytest.fixture
async def rbac_manager(di_container: AsyncContainer) -> RBACManagerInterface:
    return await di_container.get(RBACManagerInterface)


@pytest.fixture
async def app(di_container: AsyncContainer) -> FastAPI:
    if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
        del os.environ["PROMETHEUS_MULTIPROC_DIR"]

    application = test_app()
    setup_dishka(di_container, application)
    return application


def test_app() -> FastAPI:
    app = FastAPI(
        openapi_url=(
            f"{app_config.API_V1_STR}/openapi.json"
            if app_config.ENVIRONMENT in ["local", "testing"]
            else None
        ),
        lifespan=lifespan,
        redirect_slashes=False
    )

    configure_logging()
    setup_middleware(app)
    setup_router(app)

    app.add_exception_handler(Exception, handle_unknown_exception)
    app.add_exception_handler(ApplicationError, handle_application_exception)  # type: ignore
    app.add_exception_handler(RequestValidationError, handle_validation_exception) # type: ignore
    app.openapi = lambda: custom_openapi(app)
    return app


@pytest.fixture
async def client(app: FastAPI, redis_client: Redis) -> AsyncGenerator[AsyncClient]:
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
    config.addinivalue_line("markers", "e2e: E2E тесты")
    config.addinivalue_line("markers", "slow: Медленные тесты")
    config.addinivalue_line("markers", "auth: Тесты модуля аутентификации")
