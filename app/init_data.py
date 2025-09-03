from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session



async def create_first_data(db: AsyncSession) -> None:
    ...

async def init() -> None:
    async for db in get_session():
        await create_first_data(db)
        break

