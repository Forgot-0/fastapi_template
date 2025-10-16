from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission import Permission
from app.auth.schemas.permissions import PermissionListParams
from app.core.api.schemas import PaginatedResult, Pagination, SortOrder
from app.core.db.repository import BaseRepositoryMixin



@dataclass
class PermissionRepository(BaseRepositoryMixin):

    async def create(self, permission: Permission) -> None:
        self.session.add(permission)

    async def delete(self, permission: Permission) -> None:
        await self.session.delete(permission)

    async def get_permission_by_name(self, name: str) -> Permission | None:
        query = select(Permission).where(Permission.name == name)
        result = await self.session.execute(query)
        return result.scalar()