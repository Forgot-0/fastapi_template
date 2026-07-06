from datetime import timedelta
import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_config
from app.auth.exceptions import NotFoundUserError, PasswordMismatchError
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.events.service import BaseEventBus
from app.core.services.auth.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ResetPasswordCommand(BaseCommand):
    token: str
    password: str
    password_repeat: str


@dataclass(frozen=True)
class ResetPasswordCommandHandler(BaseCommandHandler[ResetPasswordCommand, None]):
    session: AsyncSession
    event_bus: BaseEventBus
    user_repository: UserRepository
    token_repository: TokenBlacklistRepository
    hash_service: HashService

    async def handle(self, command: ResetPasswordCommand) -> None:
        user_id = await self.token_repository.is_valid_token(token=command.token)

        if user_id is None:
            raise InvalidTokenError(token=command.token)

        user = await self.user_repository.get_by_id(user_id=user_id)

        if not user:
            raise NotFoundUserError(user_by="1", user_field="id")

        if command.password != command.password_repeat:
            raise PasswordMismatchError

        user.password_reset(self.hash_service.hash_password(command.password))
        await self.token_repository.invalidate_token(token=command.token)
        await self.token_repository.add_user(user.id, expiration=timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS))


        await self.session.commit()
        await self.event_bus.publish(user.pull_events())
        logger.info("Password reset", extra={"user_id": user.id, "username": user.username})
