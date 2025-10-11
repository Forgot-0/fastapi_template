from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.role import Role



@dataclass
class RoleRepository:
    session: AsyncSession

    async def get_with_permission_by_name(self, name: str) -> Role | None:
        query = select(Role).options(selectinload(Role.permissions)).where(Role.name == name)
        result = await self.session.execute(query)
        return result.scalar()