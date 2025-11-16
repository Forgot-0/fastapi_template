from dataclasses import dataclass

from app.auth.models.oauth import OAuthAccount
from app.auth.repositories.oauth import OauthAccountRepository
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetUserOAuthAccountsQuery(BaseQuery):
    user_id: int


@dataclass(frozen=True)
class GetUserOAuthAccountsQueryHandler(BaseQueryHandler[GetUserOAuthAccountsQuery, list[OAuthAccount]]):
    oauth_repository: OauthAccountRepository

    async def handle(self, query: GetUserOAuthAccountsQuery) -> list[OAuthAccount]:
        return await self.oauth_repository.get_by_user_id(query.user_id)
