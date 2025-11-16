from dataclasses import dataclass

from sqlalchemy import select

from app.auth.models.oauth import OAuthAccount
from app.core.db.repository import BaseRepositoryMixin



@dataclass
class OauthAccountRepository(BaseRepositoryMixin):
    async def create(self, oauth_account: OAuthAccount):
        self.session.add(oauth_account)

    async def get_by_id(self, account_id: int) -> OAuthAccount | None:
        query = select(OAuthAccount).where(OAuthAccount.id == account_id)
        result = await self.session.execute(query)
        return result.scalar()
