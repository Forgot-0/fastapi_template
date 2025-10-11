from dataclasses import dataclass
from datetime import datetime, timedelta
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.session import Session
from app.core.utils import now_utc



@dataclass
class SessionRepository:
    session: AsyncSession

    async def get_active_by_device(self, user_id: int, device_id: str) -> Session | None:
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.device_id == device_id,
            Session.is_active
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def deactivate_user_session(self, user_id: int, device_id: str | None) -> None:
        stmt = update(Session).where(Session.user_id == user_id, Session.device_id == device_id).values(is_active=False)
        await self.session.execute(stmt)

    async def create(self, session: Session) -> None:
        self.session.add(session)


@dataclass
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
