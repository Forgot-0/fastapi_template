from dataclasses import dataclass

from sqlalchemy import select

from app.auth.models.oauth import OAuthAccount, OAuthProviderEnum
from app.core.db.repository import BaseRepositoryMixin



@dataclass
class OauthAccountRepository(BaseRepositoryMixin):
    async def create(self, oauth_account: OAuthAccount):
        self.session.add(oauth_account)

    async def get_by_id(self, account_id: int) -> OAuthAccount | None:
        query = select(OAuthAccount).where(OAuthAccount.id == account_id)
        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_by_provider_and_user_id(
        self, provider: OAuthProviderEnum, provider_user_id: str
    ) -> OAuthAccount | None:
        """Get OAuth account by provider and provider user ID"""
        query = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id
        )
        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_by_user_id(self, user_id: int) -> list[OAuthAccount]:
        """Get all OAuth accounts for a user"""
        query = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
