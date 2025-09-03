from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services.tokens import AuthService
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class LogoutCommand(BaseCommand):
    refresh_token: str


@dataclass(frozen=True)
class LogoutCommandHandler(BaseCommandHandler[LogoutCommand, None]):
    session: AsyncSession
    token_service: AuthService

    async def handle(self, command: LogoutCommand) -> None:
        await self.token_service.logout(command.refresh_token)
        await self.session.commit()