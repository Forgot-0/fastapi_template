from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserDTO
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetUserByEmailQuery(BaseQuery):
    email: str


@dataclass(frozen=True)
class GetUserByEmailQueryHandler(BaseQueryHandler[GetUserByEmailQuery, Optional[UserDTO]]):
    session: AsyncSession
    user_repository: UserRepository

    async def handle(self, query: GetUserByEmailQuery) -> Optional[UserDTO]:
        user = await self.user_repository.get_by_email(self.session, query.email)
        if user:
            return UserDTO.model_validate(user.to_dict())
        return None