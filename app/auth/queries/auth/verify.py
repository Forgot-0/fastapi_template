from dataclasses import dataclass

from app.auth.schemas.user import UserJWTData
from app.auth.services.jwt import JWTManager
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class VerifyToken(BaseQuery):
    token: str


@dataclass(frozen=True)
class VerifyTokenHandler(BaseQueryHandler[VerifyToken, UserJWTData]):
    jwt_manager: JWTManager

    async def handle(self, query: VerifyToken) -> UserJWTData:
        token_data = await self.jwt_manager.validate_token(token=query.token)
        return UserJWTData.create_from_token(token_data)
