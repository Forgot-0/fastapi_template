from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

from app.auth.exceptions import InvalidJWTTokenException, WrongDataException
from app.auth.models.token import Token
from app.auth.models.user import User
from app.auth.repositories.token import TokenRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.token import TokenGroup
from app.auth.security import create_access_token, create_refresh_token, verify_password, verify_token
from app.auth.config import auth_config
from app.core.utils import now_utc


@dataclass
class AuthService:
    user_repository: UserRepository
    token_repository: TokenRepository

    async def create_by_user(self, user: User) -> TokenGroup:
        data={
            "sub": str(user.id),
            "device_id": str(uuid4())
        }

        access_token = create_access_token(data=data)

        jti_refresh = str(uuid4())

        refresh_token = create_refresh_token(data=data, jti=jti_refresh)

        refresh_token_create = Token(
            user_id=user.id,
            jti=jti_refresh,
            expires_at=now_utc()
            + timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS),
            device_id=data['device_id']
        )

        await self.token_repository.create(token=refresh_token_create)
        return TokenGroup(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def login(self, username: str, password: str) -> TokenGroup:
        user = await self.user_repository.get_by_username(username) or \
        await self.user_repository.get_by_email(username)

        if not user or not verify_password(password, user.password_hash):
            raise WrongDataException()

        return await self.create_by_user(user)
        

    async def get_user_by_token(self, token: str) -> User:
        token_data = verify_token(token=token, token_type="access")
        user_id = token_data.sub
        if not user_id:
            raise InvalidJWTTokenException()

        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise InvalidJWTTokenException()

        return user

    async def refresh_token(self, refresh_token: str) -> TokenGroup:
        refresh_data = verify_token(token=refresh_token, token_type="refresh")
        token = await self.token_repository.get_by_jti(refresh_data.jti)

        if not token or token.is_valid():
            raise InvalidJWTTokenException()

        new_access_token = create_access_token(
            data={"sub": str(token.user_id), 'device_id': token.device_id},
        )

        return TokenGroup(
            access_token=new_access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, refresh_token: str) -> None:
        payload = verify_token(refresh_token, token_type='refresh')
        await self.token_repository.revoke_user_device(
            user_id=int(payload.sub), jti=payload.jti
        )
