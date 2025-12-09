from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from app.core.db.session import create_async_marker, create_engine
from app.core.configs.app import app_config



class DBProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    async def get_engine(self) -> AsyncIterable[AsyncEngine]:
        engine = create_engine()
        yield engine
        await engine.dispose(close=True)

    @provide(scope=Scope.APP)
    async def get_marker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_async_marker(engine=engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, marker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with marker() as session:
            yield session

    @provide(scope=Scope.APP)
    async def get_redis(self) -> Redis:
        return Redis.from_url(app_config.redis_url)
