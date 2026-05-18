from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import uuid4

from app.auth.config import auth_config
from app.auth.dtos.tokens import TokenGroup, TokenType
from app.auth.dtos.user import AuthUserJWTData
from app.auth.repositories.session import TokenBlacklistRepository
from app.core.services.auth.dto import JwtTokenType, Token
from app.core.services.auth.exceptions import ExpiredTokenException
from app.core.services.auth.jwt_manager import JWTManager
from app.core.utils import fromtimestamp, now_utc


@dataclass
class AuthJWTManager(JWTManager):
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    token_blacklist: TokenBlacklistRepository

    def generate_payload(self, user_data: AuthUserJWTData, token_type: TokenType) -> dict[str, Any]:
        now = now_utc()
        payload = {
            "type": token_type,
            "sub": user_data.id,
            "lvl": user_data.security_level,
            "did": user_data.device_id,
            "jti": str(uuid4()),
            "exp": (
                now + timedelta(minutes=self.access_token_expire_minutes)
                if token_type == TokenType.ACCESS
                else now + timedelta(days=self.refresh_token_expire_days)
            ).timestamp(),
            "iat": now.timestamp(),
        }
        if token_type == TokenType.ACCESS:
            payload["roles"] = user_data.roles
            payload["permissions"] = user_data.permissions

        return payload

    def create_token_pair(
        self,
        security_user: AuthUserJWTData,
    ) -> TokenGroup:
        access_payload = self.generate_payload(
            security_user, TokenType.ACCESS
        )
        refresh_payload = self.generate_payload(
            security_user, TokenType.REFRESH
        )

        access_token = self.encode(access_payload)
        refresh_token = self.encode(refresh_payload)

        return TokenGroup(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, token: Token, security_user: AuthUserJWTData) -> TokenGroup:
        token_date = fromtimestamp(token.iat)

        date = await self.token_blacklist.get_token_backlist(token.jti)
        if date > token_date:
            await self.token_blacklist.add_user(
                user_id=int(token.sub),
                expiration=timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            raise ExpiredTokenException

        date = await self.token_blacklist.get_user_backlist(int(token.sub))
        if date > token_date:
            raise ExpiredTokenException

        await self.revoke_token(token)
        token_pair = self.create_token_pair(security_user=security_user)

        return token_pair

    async def revoke_token(self, token: Token) -> None:
        current_time = now_utc()
        token_exp_dt = fromtimestamp(token.exp)

        seconds_until_expiry = token_exp_dt - (current_time + timedelta(days=1))
        await self.token_blacklist.add_jwt_token(token.jti, seconds_until_expiry)

