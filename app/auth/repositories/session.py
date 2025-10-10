# app/auth/repositories/token.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models.session import Session
from app.core.utils import now_utc



@dataclass
class SessionRepository:
    session: AsyncSession

    async def get_by_jti(self, jti: str) -> Session | None:
        stmt = select(Session).where(Session.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_by_device(self, user_id: int, device_id: str) -> Session | None:
        ...

    async def get_with_user(self, jti: str) -> Session | None:
        stmt = (
            select(Session)
            .options(selectinload(Session.user))
            .where(Session.jti == jti)
            .where(Session.is_revoked == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def revoke_by_user_id(self, user_id: int) -> None:
        stmt = update(Session).where(Session.user_id == user_id).values(is_revoked=True)
        await self.session.execute(stmt)

    async def revoke_by_jti(self, jti: str) -> None:
        stmt = update(Session).where(Session.jti == jti).values(is_revoked=True)
        await self.session.execute(stmt)

    async def revoke_user_device(self, user_id: int, jti: str) -> None:
        stmt = update(Session).where(Session.jti == jti).where(Session.user_id==user_id).values(is_revoked=True)
        await self.session.execute(stmt)

    async def create(self, token: Session) -> None:
        self.session.add(token)


class TokenBlacklistRepository:
    client: Redis

    async def add_token(self, jti: str, expiration: timedelta) -> None:
        await self.client.set(
            f"revoked:{jti}",  str(expiration.total_seconds()), ex=expiration
        )

    async def is_blacklisted(self, jti: str) -> bool:
        time_str = await self.client.get(f"revoked:{jti}")
        if time_str is None:
            return False
        if now_utc() > datetime.fromtimestamp(float(time_str)):
            return False
        return True
