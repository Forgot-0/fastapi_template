from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import jwt

from app.auth.exceptions import InvalidJWTTokenException
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.schemas.token import Token, TokenGroup, TokenType
from app.auth.schemas.user import UserJWTData
from app.core.utils import now_utc



@dataclass
class JWTManager:
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    token_blacklist: TokenBlacklistRepository

    def encode(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

    def generate_payload(self, user_data: UserJWTData, token_type: TokenType) -> dict[str, Any]:
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
            payload['roles'] = user_data.roles
            payload['permissions'] = user_data.permissions

        return payload

    def create_token_pair(
        self,
        security_user: UserJWTData,
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

    async def validate_token(self, token: str) -> Token:
        payload = self.decode(token)
        token_data = Token(**payload)
        token_date = datetime.fromtimestamp(token_data.iat)

        date = await self.token_blacklist.get_token_backlist(token_data.jti)
        if date > token_date:
            raise InvalidJWTTokenException()

        date = await self.token_blacklist.get_user_backlist(int(token_data.sub))
        if date > token_date:
            raise InvalidJWTTokenException()

        return token_data

    async def refresh_tokens(self, refresh_token: str, security_user: UserJWTData) -> TokenGroup:
        await self.validate_token(refresh_token)

        token_pair = self.create_token_pair(security_user=security_user)

        return token_pair

    async def revoke_token(self, token: str) -> None:
        token_data: Token = Token(**self.decode(token))

        current_time = now_utc()
        token_exp_dt = datetime.fromtimestamp(token_data.exp,)

        seconds_until_expiry = token_exp_dt - current_time + timedelta(days=1)
        await self.token_blacklist.add_jwt_token(token_data.jti, seconds_until_expiry)
