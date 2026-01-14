from dataclasses import dataclass

from app.auth.dtos.user import AuthUserJWTData
from app.auth.services.jwt import AuthJWTManager
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class VerifyTokenQuery(BaseQuery):
    access_token: str


@dataclass(frozen=True)
class VerifyTokenQueryHandler(BaseQueryHandler[VerifyTokenQuery, AuthUserJWTData]):
    jwt_manager: AuthJWTManager

    async def handle(self, query: VerifyTokenQuery) -> AuthUserJWTData:
        token_data = await self.jwt_manager.validate_token(token=query.access_token)
        return AuthUserJWTData.create_from_token(token_data)
