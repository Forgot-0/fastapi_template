from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from app.auth.schemas.user import UserCreate
from app.auth.schemas.user import UserListParams

class UserRepository:
    async def get_by_email(self, session: AsyncSession, email: str) -> (User | None):
        result = await session.execute(User.select_not_deleted().where(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, session: AsyncSession, username: str) -> (User | None):
        result = await session.execute(User.select_not_deleted().where(User.username == username))
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, user_id: int) -> (User | None):
        result = await session.execute(User.select_not_deleted().where(User.id == user_id))
        return result.scalars().first()

    async def create(self, session: AsyncSession, data: UserCreate) -> User:
        user = User(
            username=data.username,
            email=data.email,
            password_hash=data.password_hash
        )
        session.add(user)
        return user

    async def delete_by_id(self, session: AsyncSession, user_id: int) -> None:
        user = await self.get_by_id(session=session, user_id=user_id)
        if user:
            user.soft_delete()

    async def get_list(self, session: AsyncSession, params: UserListParams) -> List[User]:
        ...