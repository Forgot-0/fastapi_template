from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import WrongDataException
from app.auth.repositories.user import UserRepository
from app.auth.security import decode_reset_token
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

    async def handle(self, command: ResetPasswordCommand) -> None:
        reset_token = decode_reset_token(token=command.token)
        user = await self.user_repository.get_by_email(email=reset_token.sub)

        if not user: return

        if command.password != command.repeat_password:
            raise WrongDataException()

        user.password_reset(command.password)
        await self.session.commit()
        await self.event_bus.publish(user.pull_events())
        logger.info("Password reset", extra={"user_id": user.id, "username": user.username})
