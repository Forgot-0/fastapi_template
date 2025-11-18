from dataclasses import dataclass
from datetime import timedelta

from redis.asyncio import Redis
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
        query = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id
        )
        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_by_user_id(self, user_id: int) -> list[OAuthAccount]:
        query = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())


@dataclass
class OAuthCodeRepository:
    client: Redis

    async def add_oauth_state(self, user_id: int, state: str) -> None:
        await self.client.set(
            f"state:{state}", user_id, ex=timedelta(minutes=10)
        )

    async def get_oauth_state(self, state: str) -> int | None:
        return await self.client.get(f"state:{state}")

    async def delete(self, state: str) -> None:
        await self.client.delete(f"state:{state}")