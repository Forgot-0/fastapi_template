from dataclasses import dataclass
from datetime import datetime, timedelta

from redis.asyncio import Redis
from sqlalchemy import select

from app.auth.models.permission import Permission
from app.core.db.repository import BaseRepositoryMixin
from app.core.utils import now_utc


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

    async def get_permissions_by_names(self, names: set[str]) -> list[Permission]:
        query = select(Permission).where(Permission.name.in_(names))
        result = await self.session.execute(query)
        return list(result.scalars().all())


@dataclass
class PermissionInvalidateRepository:
    client: Redis

    async def invalidate_permission(self, permission_name: str, expiration: timedelta | None = None) -> None:
        if expiration is None:
            expiration = timedelta(days=8)

        key = f"invalid_permission:{permission_name}"
        value = str(now_utc().timestamp())
        await self.client.set(key, value=value, ex=expiration)

    async def get_permission_invalidation_time(self, permission_name: str) -> str | None:
        key = f"invalid_permission:{permission_name}"
        return await self.client.get(key)

    async def get_max_invalidation_time(self, permission_names: list[str]) -> datetime:
        keys = [f"invalid_permission:{permission_name}" for permission_name in permission_names]
        values = await self.client.mget(*keys)
        if not values:
            return datetime.fromtimestamp(0.00)
        max_date = max(values, key=lambda x: datetime.fromtimestamp(float(x)))
        return datetime.fromtimestamp(float(max_date))

