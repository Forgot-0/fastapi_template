from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import Request, Response
from jose import jwt

from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.schemas.token import AccessToken, TokenGroup, TokenType
from app.auth.schemas.user import UserJWTData
from app.auth.services.cookie import CookieManager
from app.core.utils import now_utc



@dataclass
class JWTManager:
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    cookie_manager: CookieManager
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
                now
                + timedelta(
                    minutes=(
                        self.access_token_expire_minutes
                        if token_type == TokenType.ACCESS
                        else self.refresh_token_expire_minutes
                    )
                )
            ).timestamp(),
            "iat": now.timestamp(),
        }
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

    async def validate_token(self, token: str) -> AccessToken:
        payload = self.decode(token)
        token_data = AccessToken(**payload)

        if await self.token_blacklist.is_blacklisted(token_data.jti):
            raise

        return token_data

    async def refresh_tokens(
        self, request: Request, response: Response
    ) -> TokenGroup:
        refresh_token = self.cookie_manager.get_cookie(request, "refresh_token")

        if refresh_token is None:
            raise

        token_data = await self.validate_token(refresh_token)
        security_user = UserJWTData.create_from_token(token_data)

        token_pair = self.create_token_pair(security_user=security_user)
        self.cookie_manager.set_cookie(
            response=response,
            token=token_pair.refresh_token,
            key="refresh_token",
        )

        return token_pair

    async def revoke_token(self, response: Response, token: str) -> None:
        self.cookie_manager.delete_cookie(response, "refresh_token")

        token_data: AccessToken = AccessToken(**self.decode(token))

        current_time = now_utc()
        token_exp_dt = datetime.fromtimestamp(token_data.exp,)

        seconds_until_expiry = token_exp_dt - current_time + timedelta(days=1)
        await self.token_blacklist.add_token(token_data.sub, seconds_until_expiry)
