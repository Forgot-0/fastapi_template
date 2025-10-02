from dataclasses import dataclass
from datetime import timedelta
import logging
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_config
from app.auth.exceptions import WrongDataException
from app.auth.models.token import Token
from app.auth.repositories.token import TokenRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.token import TokenGroup
from app.auth.security import create_access_token, create_refresh_token, verify_password
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.utils import now_utc


logger = logging.getLogger(__name__)

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
        user = await self.user_repository.get_by_username(command.username) or \
        await self.user_repository.get_by_email(command.username)

        if not user or not verify_password(command.password, user.password_hash):
            raise WrongDataException()

        data={
            "sub": str(user.id),
            "device_id": uuid4().hex
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
        await self.session.commit()

        logger.info("Logining user", extra={"user_id": user.id, "device_id": data['device_id']})

        return TokenGroup(
            access_token=access_token,
            refresh_token=refresh_token
        )