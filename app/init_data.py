import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission import Permission
from app.auth.models.role import Role
from app.auth.models.role_permission import RolesEnum
from app.core.db.session import get_session



async def create_first_data(db: AsyncSession) -> None:
    roles = RolesEnum.get_all_roles()
    for base_role in roles:
        role = await db.execute(select(Role).where(Role.name==base_role.name))

        if role.scalar() is None:
            db.add(base_role)
    await db.commit()



async def init_data() -> None:
    async for db in get_session():
        await create_first_data(db)
        break

