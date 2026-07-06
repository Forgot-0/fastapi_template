from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import uuid4

from app.auth.config import auth_config
from app.auth.dtos.tokens import TokenGroup, TokenType
from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import NotFoundOrInactiveSessionError, TokenInBlacklistError
from app.auth.repositories.session import TokenBlacklistRepository
from app.core.services.auth.dto import Token
from app.core.services.auth.jwt_manager import JWTManager
from app.core.utils import fromtimestamp, now_utc


@dataclass
class AuthJWTManager(JWTManager):
    token_blacklist: TokenBlacklistRepository

    def generate_payload(self, user_data: AuthUserJWTData, token_type: TokenType) -> dict[str, Any]:
        now = now_utc()
        payload = {
            "type": token_type,
            "sub": user_data.id,
            "username": user_data.username,
            "lvl": user_data.security_level,
            "did": user_data.device_id,
            "jti": str(uuid4()),
            "exp": (
                now + timedelta(minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES)
                if token_type == TokenType.ACCESS
                else now + timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS)
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

    async def refresh_tokens(self, refresh_token: Token, security_user: AuthUserJWTData) -> TokenGroup:
        token_iat_dt = fromtimestamp(refresh_token.iat)

        blacklisted_token_date = await self.token_blacklist.get_token_backlist(refresh_token.jti)
        if blacklisted_token_date and blacklisted_token_date > token_iat_dt:
            raise TokenInBlacklistError

        blacklisted_user_date = await self.token_blacklist.get_user_backlist(int(refresh_token.sub))
        if blacklisted_user_date and blacklisted_user_date > token_iat_dt:
            raise TokenInBlacklistError

        await self.revoke_token(refresh_token)

        return self.create_token_pair(security_user=security_user)

    async def revoke_token(self, token: Token) -> None:

        current_time = now_utc()
        token_exp_dt = fromtimestamp(token.exp)

        seconds_until_expiry = token_exp_dt - current_time
        await self.token_blacklist.add_jwt_token(token.jti, seconds_until_expiry)

