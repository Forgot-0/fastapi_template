from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import uuid4

from jose import ExpiredSignatureError, JWTError, jwt

from app.auth.dtos.tokens import TokenGroup, TokenType
from app.auth.dtos.user import AuthUserJWTData
from app.auth.repositories.session import TokenBlacklistRepository
from app.core.services.auth.dto import JwtTokenType
from app.core.services.auth.exceptions import ExpiredTokenException, InvalidTokenException
from app.core.services.auth.jwt_manager import JWTManager
from app.core.utils import fromtimestamp, now_utc


@dataclass
class AuthJWTManager(JWTManager):
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    token_blacklist: TokenBlacklistRepository

    def encode(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        try:
            data = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except ExpiredSignatureError as err:
            raise ExpiredTokenException(token=token) from err
        except JWTError as err:
            raise InvalidTokenException(token=token) from err
        return data

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

    async def refresh_tokens(self, refresh_token: str, security_user: AuthUserJWTData) -> TokenGroup:
        token = await self.validate_token(refresh_token, token_type=JwtTokenType.REFRESH)
        token_date = fromtimestamp(token.iat)

        date = await self.token_blacklist.get_token_backlist(token.jti)
        if date > token_date:
            raise ExpiredTokenException(token=refresh_token)

        date = await self.token_blacklist.get_user_backlist(int(token.sub))
        if date > token_date:
            raise ExpiredTokenException(token=refresh_token)

        await self.revoke_token(refresh_token)
        token_pair = self.create_token_pair(security_user=security_user)

        return token_pair

    async def revoke_token(self, token: str) -> None:
        token_data = await self.validate_token(token, JwtTokenType.REFRESH)

        current_time = now_utc()
        token_exp_dt = fromtimestamp(token_data.exp)

        seconds_until_expiry = token_exp_dt - (current_time + timedelta(days=1))
        await self.token_blacklist.add_jwt_token(token_data.jti, seconds_until_expiry)

