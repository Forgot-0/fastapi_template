from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services.users import UserService
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class VerifyCommand(BaseCommand):
    token: str


@dataclass(frozen=True)
class VerifyCommandHandler(BaseCommandHandler[VerifyCommand, None]):
    session: AsyncSession
    user_service: UserService

    async def handle(self, command: VerifyCommand) -> None:
        await self.user_service.verify(command.token)
        await self.session.commit()