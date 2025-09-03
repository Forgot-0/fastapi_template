from dataclasses import dataclass

from app.auth.schemas.user import UserDTO
from app.auth.services.tokens import AuthService
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetByAccessTokenQuery(BaseQuery):
    token: str


@dataclass(frozen=True)
class GetByAccessTokenQueryHandler(BaseQueryHandler[GetByAccessTokenQuery, UserDTO]):
    token_service: AuthService

    async def handle(self, query: GetByAccessTokenQuery) -> UserDTO:
        user = await self.token_service.get_user_by_token(query.token)
        return UserDTO.model_validate(user.to_dict())