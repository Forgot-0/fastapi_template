from dataclasses import dataclass
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from app.auth.schemas.user import UserCreate
from app.auth.schemas.user import UserListParams

@dataclass
class UserRepository:
    session: AsyncSession

    async def get_by_email(self, email: str) -> (User | None):
        result = await self.session.execute(User.select_not_deleted().where(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> (User | None):
        result = await self.session.execute(User.select_not_deleted().where(User.username == username))
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> (User | None):
        result = await self.session.execute(User.select_not_deleted().where(User.id == user_id))
        return result.scalars().first()

    async def create(self, user: User) -> None:
        self.session.add(user)

    async def delete_by_id(self, user_id: int) -> None:
        user = await self.get_by_id(user_id=user_id)
        if user:
            user.soft_delete()

    async def get_list(self, params: UserListParams) -> List[User]:
        ...