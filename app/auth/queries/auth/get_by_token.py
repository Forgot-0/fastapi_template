from dataclasses import dataclass
import logging

from app.auth.exceptions import InvalidJWTTokenException
from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.services.jwt import JWTManager
from app.core.queries import BaseQuery, BaseQueryHandler


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class GetByAccessTokenQuery(BaseQuery):
    token: str


@dataclass(frozen=True)
class GetByAccessTokenQueryHandler(BaseQueryHandler[GetByAccessTokenQuery, User]):
    user_repository: UserRepository
    jwt_manager: JWTManager

    async def handle(self, query: GetByAccessTokenQuery) -> User:
        token_data = await self.jwt_manager.validate_token(token=query.token)
        user_id = token_data.sub
        if not user_id:
            raise InvalidJWTTokenException()

        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise InvalidJWTTokenException()

        logger.debug("Get user by access token", extra={"user_id": user.id})
        return user