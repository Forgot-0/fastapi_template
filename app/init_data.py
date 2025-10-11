import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission import Permission
from app.auth.models.role import Role
from app.core.db.session import get_session



async def create_first_data(db: AsyncSession) -> None:
    role = await db.execute(select(Role).where(Role.name=="user"))

    if not role.scalar():
        role = Role(
            name="user",
            description="",
            security_level=1
        )

        role.add_permission(
            Permission(
                name="user:read"
            )
        )
        db.add(role)

        await db.commit()


async def main() -> None:
    async for db in get_session():
        await create_first_data(db)
        break


if __name__ == '__main__':
    asyncio.run(main())