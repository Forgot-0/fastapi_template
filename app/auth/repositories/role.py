from dataclasses import dataclass
from datetime import datetime, timedelta

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.models.role import Role
from app.core.db.repository import BaseRepositoryMixin
from app.core.utils import now_utc



@dataclass
class RoleRepository(BaseRepositoryMixin):

    async def get_with_permission_by_name(self, name: str) -> Role | None:
        query = select(Role).options(selectinload(Role.permissions)).where(Role.name == name)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_by_name(self, name: str) -> Role | None:
        query = select(Role).where(Role.name==name)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_by_id(self, role_id: int) -> Role | None:
        query = select(Role).where(Role.id==role_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def create(self, role: Role) -> None:
        self.session.add(role)


@dataclass
class RoleInvalidateRepository:
    client: Redis

    async def invalidate_role(self, role_name: str, expiration: timedelta | None = None) -> None:
        if expiration is None:
            expiration = timedelta(days=8)

        key = f"invalid_role:{role_name}"
        value = str(now_utc().timestamp())
        await self.client.set(key, value=value, ex=expiration)

    async def get_role_invalidation_time(self, role_name: str) -> str | None:
        key = f"invalid_role:{role_name}"
        return await self.client.get(key)

    async def get_max_invalidation_time(self, role_names: list[str]) -> datetime:
        keys = [f"invalid_role:{permission_name}" for permission_name in role_names]
        values = await self.client.mget(*keys)
        if not values:
            return datetime.fromtimestamp(0.00)
        max_date = max(values, key=lambda x: datetime.fromtimestamp(float(x)))
        return datetime.fromtimestamp(float(max_date))
