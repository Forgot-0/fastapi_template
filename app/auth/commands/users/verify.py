from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import WrongDataException
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

    async def handle(self, command: VerifyCommand) -> None:
        # verify_token = decode_verify_token(token=command.token)
        # user = await self.user_repository.get_by_email(email=verify_token.sub)

        # if not user:
        #     raise WrongDataException()

        # user.verify()
        # await self.session.commit()
        # await self.event_bus.publish(user.pull_events())
        # logger.info("Verify", extra={"email": user.email, "user_id": user.id})
        ...