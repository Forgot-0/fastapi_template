from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.events.service import BaseEventBus


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class VerifyCommand(BaseCommand):
    token: str


@dataclass(frozen=True)
class VerifyCommandHandler(BaseCommandHandler[VerifyCommand, None]):
    session: AsyncSession
    event_bus: BaseEventBus
    user_repository: UserRepository
    token_repository: TokenBlacklistRepository

    async def handle(self, command: VerifyCommand) -> None:
        user_id = await self.token_repository.is_valid_token(token=command.token)

        if user_id is None:
            raise

        user = await self.user_repository.get_by_id(user_id=user_id)

        if not user:
            raise 

        user.verify()
        await self.token_repository.invalidate_token(command.token)

        await self.session.commit()
        await self.event_bus.publish(user.pull_events())

        logger.info("Verify", extra={"email": user.email, "user_id": user.id})
