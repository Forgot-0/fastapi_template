from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.repositories.token import TokenRepository
from app.auth.schemas.user import UserDTO
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetCurrentUserQuery(BaseQuery):
    token: str


@dataclass(frozen=True)
class GetCurrentUserQueryHandler(BaseQueryHandler[GetCurrentUserQuery, Optional[UserDTO]]):
    session: AsyncSession
    user_repository: UserRepository
    token_repository: TokenRepository

    async def handle(self, query: GetCurrentUserQuery) -> Optional[UserDTO]:
        # Validate token and get user
        token_data = await self.token_repository.get_by_token(self.session, query.token)
        if not token_data or not token_data.is_valid():
            return None
        
        user = await self.user_repository.get_by_id(self.session, token_data.user_id)
        if user:
            return UserDTO.model_validate(user.to_dict())
        return None