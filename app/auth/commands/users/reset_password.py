import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidTokenException, NotFoundUserException, PasswordMismatchException
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.events.service import BaseEventBus

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ResetPasswordCommand(BaseCommand):
    token: str
    password: str
    repeat_password: str


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
            raise InvalidTokenException(token=command.token)

        user = await self.user_repository.get_by_id(user_id=user_id)

        if not user:
            raise NotFoundUserException(user_by="1", user_field="id")

        if command.password != command.repeat_password:
            raise PasswordMismatchException

        user.password_reset(self.hash_service.hash_password(command.password))
        await self.token_repository.invalidate_token(token=command.token)

        await self.session.commit()
        await self.event_bus.publish(user.pull_events())
        logger.info("Password reset", extra={"user_id": user.id, "username": user.username})
