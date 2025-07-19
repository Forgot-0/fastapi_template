from typing import AsyncIterable
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from app.core.db.session import create_async_marker, create_engine






class DBProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_engine(self) -> AsyncIterable[AsyncEngine]:
        engine = create_engine()
        yield engine
        await engine.dispose(True)

    @provide
    async def get_marker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_async_marker(engine=engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, marker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with marker() as session:
            yield session
