# app/auth/repositories/token.py

from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models.token import Token
from app.auth.schemas.token import RefreshTokenCreate



class TokenRepository:
    async def get_by_token(self, session: AsyncSession, jti: str) -> Token | None:
        stmt = select(Token).where(Token.jti == jti)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_with_user(self, session: AsyncSession, jti: str) -> Token | None:
        now = datetime.now()
        stmt = (
            select(Token)
            .options(selectinload(Token.user))
            .where(Token.jti == jti)
            .where(Token.is_revoked == False)
            .where(Token.expires_at > now)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def revoke_by_user_id(self, session: AsyncSession, user_id: int) -> None:
        stmt = update(Token).where(Token.user_id == user_id).values(is_revoked=True)
        await session.execute(stmt)

    async def revoke_by_jti(self, session: AsyncSession, jti: str) -> None:
        stmt = update(Token).where(Token.jti == jti).values(is_revoked=True)
        await session.execute(stmt)

    async def revoke_user_device(self, session: AsyncSession, user_id: int, device_id: str) -> None:
        stmt = update(Token).where(Token.user_id == user_id).where(Token.device_id == device_id).values(is_revoked=True)
        await session.execute(stmt)

    async def create(self, session: AsyncSession, token_data: RefreshTokenCreate) -> None:
        token = Token(
            user_id=token_data.user_id,
            jti=token_data.jti,
            device_id=token_data.device_id,
            expires_at=token_data.expires_at
        )
        session.add(token)
