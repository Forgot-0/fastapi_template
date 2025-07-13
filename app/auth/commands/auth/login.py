from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_config
from app.auth.repositories.token import TokenRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.token import RefreshTokenCreate, TokenGroup
from app.auth.security import create_access_token, create_refresh_token, verify_password
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class LoginCommand(BaseCommand):
    username: str
    password: str


@dataclass(frozen=True)
class LoginCommandHandler(BaseCommandHandler[LoginCommand, TokenGroup]):
    session: AsyncSession
    user_repository: UserRepository
    token_repository: TokenRepository

    async def handle(self, command: LoginCommand) -> TokenGroup:
        user = await self.user_repository.get_by_username(
            self.session, command.username
        ) or await self.user_repository.get_by_email(self.session, command.username)

        if not user or not verify_password(command.password, user.password_hash):
            raise 

        if not user.is_active:
            raise 

        if not user.is_verified:
            raise 

        data={
            "sub": str(user.id),
            "device_id": str(uuid4())
        }

        access_token = create_access_token(data=data)

        jti_refresh = str(uuid4())

        refresh_token = create_refresh_token(data=data, jti=jti_refresh)

        refresh_token_create = RefreshTokenCreate(
            jti=jti_refresh,
            user_id=user.id,
            expires_at=datetime.now()
            + timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS),
            device_id=data['device_id']
        )

        await self.token_repository.create(self.session, token_data=refresh_token_create)
        await self.session.commit()
        return TokenGroup(access_token=access_token, refresh_token=refresh_token)