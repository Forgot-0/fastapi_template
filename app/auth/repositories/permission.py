from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission import Permission



@dataclass
class PermissionRepository:
    session: AsyncSession

    async def get_permission_by_name(self, name: str) -> Permission | None:
        query = select(Permission).where(Permission.name == name)
        result = await self.session.execute(query)
        return result.scalar()

    async def create(self, permission: Permission) -> None:
        self.session.add(permission)
