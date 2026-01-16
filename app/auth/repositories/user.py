from dataclasses import dataclass

from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload

from app.auth.filters.users import UserFilter
from app.auth.models.permission import Permission
from app.auth.models.role import Role
from app.auth.models.user import User
from app.core.db.repository import IRepository


@dataclass
class UserRepository(IRepository[User]):
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
        results = await self.session.execute(query)
        return results.scalar()

    async def get_user_with_permission_by_id(self, user_id: int) -> User | None:
        query = select(User).options(
           selectinload(User.permissions), selectinload(User.roles).selectinload(Role.permissions)
        ).where(User.id == user_id)
        results = await self.session.execute(query)
        return results.scalar()

    async def create(self, user: User) -> None:
        self.session.add(user)

    async def delete_by_id(self, user_id: int) -> None:
        user = await self.get_by_id(user_id=user_id)
        if user:
            user.soft_delete()

    def apply_relationship_filters(self, stmt: Select, filters: UserFilter) -> Select:

        if filters.role_names:
            stmt = stmt.join(User.roles).where(Role.name.in_(filters.role_names))

        if filters.permission_names:
            stmt = stmt.join(User.permissions).where(Permission.name.in_(filters.permission_names))

        return stmt
