from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserDTO
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetUserByIdQuery(BaseQuery):
    user_id: int


@dataclass(frozen=True)
class GetUserByIdQueryHandler(BaseQueryHandler[GetUserByIdQuery, Optional[UserDTO]]):
    session: AsyncSession
    user_repository: UserRepository

    async def handle(self, query: GetUserByIdQuery) -> Optional[UserDTO]:
        user = await self.user_repository.get_by_id(self.session, query.user_id)
        if user:
            return UserDTO.model_validate(user.to_dict())
        return None