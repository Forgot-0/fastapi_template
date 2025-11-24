from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.configs.app import app_config

engine = create_async_engine(
    url=str(app_config.postgres_url),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=app_config.SQL_ECHO,
    future=True,
)

def create_engine() -> AsyncEngine:
    return create_async_engine(
            str(app_config.postgres_url),
            pool_pre_ping=True,
            pool_size=15,
            max_overflow=10,
            echo=app_config.SQL_ECHO,
            pool_recycle=3600,
            future=True,
        )

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

def create_async_marker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

