from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services.users import UserService
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class SendVerifyCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendVerifyCommandHandler(BaseCommandHandler[SendVerifyCommand, None]):
    session: AsyncSession
    user_service: UserService

    async def handle(self, command: SendVerifyCommand) -> None:
        await self.user_service.send_verify(command.email)