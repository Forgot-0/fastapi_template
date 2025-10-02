from dataclasses import dataclass
import logging

from app.auth.exceptions import InvalidJWTTokenException
from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.security import verify_token
from app.core.queries import BaseQuery, BaseQueryHandler


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class GetByAccessTokenQuery(BaseQuery):
    token: str


@dataclass(frozen=True)
class GetByAccessTokenQueryHandler(BaseQueryHandler[GetByAccessTokenQuery, User]):
    user_repository: UserRepository

    async def handle(self, query: GetByAccessTokenQuery) -> User:
        token_data = verify_token(token=query.token, token_type="access")
        user_id = token_data.sub
        if not user_id:
            raise InvalidJWTTokenException()

        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise InvalidJWTTokenException()

        return user