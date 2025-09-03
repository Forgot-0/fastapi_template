from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services.users import UserService
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class SendResetPasswordCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendResetPasswordCommandHandler(BaseCommandHandler[SendResetPasswordCommand, None]):
    session: AsyncSession
    user_service: UserService

    async def handle(self, command: SendResetPasswordCommand) -> None:
        await self.user_service.send_reset_password(command.email)