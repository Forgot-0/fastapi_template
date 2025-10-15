from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission import Permission
from app.auth.schemas.permissions import PermissionListParams
from app.core.api.schemas import PaginatedResult, Pagination, SortOrder



@dataclass
class PermissionRepository:
    session: AsyncSession

    async def get_permission_by_name(self, name: str) -> Permission | None:
        query = select(Permission).where(Permission.name == name)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_list(self, params: PermissionListParams) -> PaginatedResult[Permission]:
        query = select(Permission)
        if params.filters:
            for item in params.filters:
                if isinstance(item.value, list):
                    query = query.where(getattr(Permission, item.field).in_(item.value))
                else:
                    query = query.where(getattr(Permission, item.field) == item.value)  # type: ignore

        if params.sort:
            for item in params.sort:
                column = getattr(Permission, item.field)
                query = query.order_by(column.desc() if item.order == SortOrder.desc else column)

        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        if total is None:
            total = 0

        query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
        result = await self.session.execute(query)
        items = result.scalars().all()
        return PaginatedResult(
            items=list(items),
            pagination=Pagination(total=total, page=params.page, page_size=params.page_size),
        )

    async def create(self, permission: Permission) -> None:
        self.session.add(permission)

    async def delete(self, permission: Permission) -> None:
        await self.session.delete(permission)
