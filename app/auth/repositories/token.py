# app/auth/repositories/token.py

from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models.token import Token



@dataclass
class TokenRepository:
    session: AsyncSession

    async def get_by_jti(self, jti: str) -> Token | None:
        stmt = select(Token).where(Token.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_with_user(self, jti: str) -> Token | None:
        stmt = (
            select(Token)
            .options(selectinload(Token.user))
            .where(Token.jti == jti)
            .where(Token.is_revoked == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def revoke_by_user_id(self, user_id: int) -> None:
        stmt = update(Token).where(Token.user_id == user_id).values(is_revoked=True)
        await self.session.execute(stmt)

    async def revoke_by_jti(self, jti: str) -> None:
        stmt = update(Token).where(Token.jti == jti).values(is_revoked=True)
        await self.session.execute(stmt)

    async def revoke_user_device(self, user_id: int, jti: str) -> None:
        stmt = update(Token).where(Token.jti == jti).where(Token.user_id==user_id).values(is_revoked=True)
        await self.session.execute(stmt)

    async def create(self, token: Token) -> None:
        self.session.add(token)
