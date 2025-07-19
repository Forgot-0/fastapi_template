from dataclasses import dataclass
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserDTO, UserListParams
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetUserListQuery(BaseQuery):
    params: UserListParams


@dataclass(frozen=True)
class GetUserListQueryHandler(BaseQueryHandler[GetUserListQuery, List[UserDTO]]):
    session: AsyncSession
    user_repository: UserRepository

    async def handle(self, query: GetUserListQuery) -> List[UserDTO]:
        users = await self.user_repository.get_list(self.session, query.params)
        return [UserDTO.model_validate(user.to_dict()) for user in users]