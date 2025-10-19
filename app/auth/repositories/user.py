from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.role import Role
from app.auth.models.user import User
from app.core.db.repository import BaseRepositoryMixin



@dataclass
class UserRepository(BaseRepositoryMixin):
    session: AsyncSession

    async def get_by_email(self, email: str) -> (User | None):
        result = await self.session.execute(User.select_not_deleted().where(User.email == email))
        return result.scalars().first()

    async def get_with_roles_by_email(self, email: str) -> (User | None):
        result = await self.session.execute(
            User.select_not_deleted().options(
                selectinload(User.permissions), selectinload(User.roles).selectinload(Role.permissions)
            ).where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> (User | None):
        result = await self.session.execute(User.select_not_deleted().where(User.username == username))
        return result.scalars().first()

    async def get_with_roles_by_username(self, username: str) -> (User | None):
        result = await self.session.execute(
            User.select_not_deleted().options(
                selectinload(User.permissions), selectinload(User.roles).selectinload(Role.permissions)
            ).where(User.username == username)
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> (User | None):
        result = await self.session.execute(User.select_not_deleted().where(User.id == user_id))
        return result.scalars().first()

    async def get_user_with_roles_by_id(self, user_id: int) -> User | None:
        query = select(User).options(selectinload(User.roles)).where(User.id == user_id)
        reults = await self.session.execute(query)
        return reults.scalar()

    async def get_user_with_permission_by_id(self, user_id: int) -> User | None:
        query = select(User).options(
           selectinload(User.permissions), selectinload(User.roles).selectinload(Role.permissions)
        ).where(User.id == user_id)
        reults = await self.session.execute(query)
        return reults.scalar()

    async def create(self, user: User) -> None:
        self.session.add(user)

    async def delete_by_id(self, user_id: int) -> None:
        user = await self.get_by_id(user_id=user_id)
        if user:
            user.soft_delete()
